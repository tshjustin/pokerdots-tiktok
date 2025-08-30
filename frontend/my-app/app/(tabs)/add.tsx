// app/(tabs)/add.tsx
import React, { useCallback, useMemo, useRef, useState, useEffect } from "react";
import { View, Text, StyleSheet, Pressable, ActivityIndicator, Alert } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import * as ImagePicker from "expo-image-picker";
import * as ExpoCam from "expo-camera";
import { useCameraPermissions, useMicrophonePermissions } from "expo-camera";
import { useVideoPlayer, VideoView, type VideoSource } from "expo-video";

// ---- CONFIG ----
const API_BASE = process.env.EXPO_PUBLIC_API_BASE ?? "http://localhost:4000";
type PresignedPost = { url: string; fields: Record<string, string>; key?: string };

// Camera compat (new CameraView or legacy Camera)
const CameraCompat: any = (ExpoCam as any).CameraView ?? (ExpoCam as any).Camera;
const isNewCameraApi = Boolean((ExpoCam as any).CameraView);

export default function AddPage() {
  // selected/recorded asset
  const [asset, setAsset] = useState<{ uri: string; name: string; type: string } | null>(null);

  // upload state
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  // camera permissions
  const [camPerm, requestCamPerm] = useCameraPermissions();
  const [micPerm, requestMicPerm] = useMicrophonePermissions();

  // camera ref + recording state
  const camRef = useRef<any>(null);
  const [recording, setRecording] = useState(false);

  // ask permissions on focus
  useFocusEffect(
    useCallback(() => {
      (async () => {
        if (!asset) {
          if (!camPerm?.granted) await requestCamPerm();
          if (!micPerm?.granted) await requestMicPerm();
        }
      })();
    }, [asset, camPerm?.granted, micPerm?.granted, requestCamPerm, requestMicPerm])
  );

  // ---------- VIDEO PLAYER (always call this hook) ----------
  const source: VideoSource = useMemo(
    () => (asset ? { uri: asset.uri, useCaching: true } : { uri: "" as any }),
    [asset?.uri]
  );
  const player = useVideoPlayer(source, (p) => {
    p.loop = true;
    p.muted = false;
    p.audioMixingMode = "mixWithOthers";
  });
  useEffect(() => {
    if (asset) player.play(); else player.pause();
  }, [asset, player]);

  // ---------- record handlers (support both APIs) ----------
  const startRecording = async () => {
    if (!camRef.current || recording) return;
    try {
      setRecording(true);
      if (isNewCameraApi) {
        camRef.current.startRecording({
          maxDuration: 60,
          onRecordingFinished: ({ uri }: { uri: string }) => {
            setRecording(false);
            setAsset({ uri, name: guessName(uri, "record.mp4"), type: "video/mp4" });
          },
          onRecordingError: (e: any) => {
            setRecording(false);
            Alert.alert("Record error", String(e?.message ?? e));
          },
        });
      } else {
        const video = await camRef.current.recordAsync({
          maxDuration: 60,
          quality: "1080p",
          mute: false,
        });
        setRecording(false);
        setAsset({ uri: video.uri, name: guessName(video.uri, "record.mp4"), type: "video/mp4" });
      }
    } catch (e: any) {
      setRecording(false);
      Alert.alert("Record error", String(e?.message ?? e));
    }
  };
  const stopRecording = () => camRef.current?.stopRecording?.();

  // pick from gallery
  const pickVideo = async () => {
    try {
      const lib = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!lib.granted) throw new Error("Library permission denied");
      const res = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Videos,
        quality: 1,
      });
      if (res.canceled) return;
      const a = res.assets[0];
      setAsset({
        uri: a.uri,
        name: a.fileName ?? guessName(a.uri, "upload.mp4"),
        type: a.mimeType ?? "video/mp4",
      });
    } catch (e: any) {
      Alert.alert("Picker error", e?.message ?? String(e));
    }
  };

  // upload to S3
  const onPost = async () => {
    if (!asset) return;
    try {
      setUploading(true);
      setProgress(0);
      const ps = await presign();
      await uploadToS3WithPresignedPost(ps, asset, setProgress);
      await commit(ps.fields.key ?? ps.key ?? "");
      Alert.alert("Uploaded!", "Your video will appear in the feed once processed.");
      setAsset(null);
      setProgress(0);
    } catch (e: any) {
      Alert.alert("Upload failed", e?.message ?? String(e));
    } finally {
      setUploading(false);
    }
  };

  const onRetake = () => setAsset(null);

  // ---------- render ----------
  // permissions gate
  if (!camPerm?.granted || !micPerm?.granted) {
    return (
      <View style={styles.centerRoot}>
        <Text style={styles.permissionTitle}>Camera & Microphone required</Text>
        <View style={{ height: 12 }} />
        <Pressable style={styles.btnPrimary} onPress={async () => {
          await requestCamPerm(); await requestMicPerm();
        }}>
          <Text style={styles.btnText}>Grant permissions</Text>
        </Pressable>
        <View style={{ height: 8 }} />
        <Pressable style={styles.btnSecondary} onPress={pickVideo}>
          <Text style={styles.btnText}>Pick from gallery instead</Text>
        </Pressable>
      </View>
    );
  }

  // camera mode
  if (!asset) {
    return (
      <View style={styles.cameraRoot}>
        <CameraCompat
          ref={camRef}
          style={StyleSheet.absoluteFill}
          {...(isNewCameraApi
            ? { mode: "video", facing: "back", videoStabilizationMode: "auto", animateShutter: false, mute: false }
            : { type: (ExpoCam as any).CameraType?.back, ratio: "16:9" })}
        />

        {/* bottom controls */}
        <View style={styles.bottomBar}>
          <Pressable onPress={pickVideo} style={styles.galleryBtn} hitSlop={12}>
            <View style={styles.galleryIcon} />
          </Pressable>

          <Pressable
            onPress={recording ? stopRecording : startRecording}
            style={[styles.shutterOuter, recording && styles.shutterOuterRec]}
            hitSlop={10}
          >
            <View style={[styles.shutterInner, recording && styles.shutterInnerRec]} />
          </Pressable>

          <View style={{ width: 48 }} />
        </View>
      </View>
    );
  }

  // preview mode
  return (
    <View style={styles.previewRoot}>
      <View style={styles.previewStage}>
        {/* Only render VideoView when we have an asset */}
        <VideoView
          player={player}
          style={{ flex: 1 }}
          contentFit="cover"
          contentPosition={{ dx: 0.5, dy: 0.5 }}
          allowsFullscreen={false}
          allowsPictureInPicture={false}
        />
      </View>

      <View style={styles.previewActions}>
        {!uploading ? (
          <>
            <Pressable style={styles.btnSecondary} onPress={onRetake}>
              <Text style={styles.btnText}>Retake</Text>
            </Pressable>
            <View style={{ width: 10 }} />
            <Pressable style={styles.btnPrimary} onPress={onPost}>
              <Text style={styles.btnText}>Post</Text>
            </Pressable>
          </>
        ) : (
          <View style={styles.uploadRow}>
            <ActivityIndicator />
            <Text style={styles.progress}>{Math.round(progress * 100)}%</Text>
          </View>
        )}
      </View>
    </View>
  );
}

// ---------- helpers ----------
function guessName(uri: string, fallback: string) {
  try {
    const seg = uri.split(/[\\/]/).pop() || fallback;
    return seg.includes(".") ? seg : fallback;
  } catch { return fallback; }
}

async function presign(): Promise<PresignedPost> {
  const resp = await fetch(`${API_BASE}/presign`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userId: "demo-user" }),
  });
  if (!resp.ok) throw new Error(`presign failed: ${resp.status}`);
  return resp.json();
}

function uploadToS3WithPresignedPost(
  presigned: PresignedPost,
  file: { uri: string; name: string; type: string },
  onProgress?: (p: number) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const form = new FormData();
    Object.entries(presigned.fields).forEach(([k, v]) => form.append(k, v));
    if (presigned.fields["Content-Type"] && presigned.fields["Content-Type"] !== file.type) {
      return reject(new Error("Content-Type mismatch vs policy"));
    }
    form.append("file", { uri: file.uri, name: file.name, type: file.type } as any);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", presigned.url);
    xhr.upload.onprogress = (evt) => {
      if (evt.lengthComputable && onProgress) onProgress(evt.loaded / evt.total);
    };
    xhr.onload = () => {
      const ok = xhr.status === 204 || xhr.status === 201;
      if (!ok) return reject(new Error(`S3 upload failed: ${xhr.status} ${xhr.responseText}`));
      resolve();
    };
    xhr.onerror = () => reject(new Error("Network error during upload"));
    xhr.send(form);
  });
}

async function commit(s3Key: string) {
  try {
    await fetch(`${API_BASE}/videos/commit`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ s3Key }),
    });
  } catch {}
}

// ---------- styles ----------
const styles = StyleSheet.create({
  cameraRoot: { flex: 1, backgroundColor: "black" },
  previewRoot: { flex: 1, backgroundColor: "black" },
  previewStage: { flex: 1, overflow: "hidden" },
  previewActions: { padding: 16, flexDirection: "row", justifyContent: "center", alignItems: "center" },

  bottomBar: {
    position: "absolute", left: 0, right: 0, bottom: 28,
    flexDirection: "row", alignItems: "center", justifyContent: "space-between",
    paddingHorizontal: 24,
  },

  shutterOuter: {
    width: 74, height: 74, borderRadius: 74, borderWidth: 6, borderColor: "#fff",
    alignItems: "center", justifyContent: "center",
  },
  shutterInner: { width: 56, height: 56, borderRadius: 56, backgroundColor: "#fff" },
  shutterOuterRec: { borderColor: "#ff453a" },
  shutterInnerRec: { backgroundColor: "#ff453a" },

  galleryBtn: {
    width: 48, height: 48, borderRadius: 12, overflow: "hidden",
    backgroundColor: "rgba(255,255,255,0.25)", alignItems: "center", justifyContent: "center",
  },
  galleryIcon: { width: 28, height: 20, borderWidth: 2, borderColor: "#fff", borderRadius: 4 },

  btnPrimary: { backgroundColor: "#007AFF", paddingHorizontal: 16, paddingVertical: 12, borderRadius: 12 },
  btnSecondary: { backgroundColor: "#3A3A3C", paddingHorizontal: 16, paddingVertical: 12, borderRadius: 12 },
  btnText: { color: "white", fontWeight: "600" },

  centerRoot: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: "black" },
  permissionTitle: { color: "white", fontSize: 16, fontWeight: "600" },
  uploadRow: { flexDirection: "row", gap: 8, alignItems: "center" },
  progress: { color: "white", marginLeft: 8 },
});

import { Modal, View, Text, StyleSheet, Pressable, FlatList, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export type TokenOffer = {
  id: string;
  tokens: number;
  kind: 'ad' | 'purchase';
  priceUsd?: number;
  icon: any; // will hold a require() reference
};

type Props = {
  visible: boolean;
  onClose: () => void;
  remaining: number;
  offers: TokenOffer[];
  onSelectOffer?: (offer: TokenOffer) => void;
};

export default function GetMoreTokensModal({
  visible,
  onClose,
  remaining,
  offers,
  onSelectOffer,
}: Props) {
  return (
    <Modal visible={visible} transparent animationType="fade" statusBarTranslucent>
      <View style={s.backdrop}>
        <View style={s.sheet}>
          {/* Close */}
          <Pressable style={s.closeBtn} onPress={onClose} hitSlop={10}>
            <Ionicons name="close" size={24} color="#111" />
          </Pressable>

          <Text style={s.title}>Get More Tokens</Text>
          <Text style={s.subtitle}>
            You have <Text style={s.highlight}>{remaining} tokens</Text> now
          </Text>
          <Text style={s.caption}>All money will be contributed to the appreciation pool</Text>

          <FlatList
            data={offers}
            keyExtractor={(o) => o.id}
            ItemSeparatorComponent={() => <View style={s.separator} />}
            renderItem={({ item }) => (
                <View style={s.row}>
                {/* Left icon + label */}
                <View style={s.left}>
                    <Image source={item.icon} style={s.icon} resizeMode="contain" />
                    <Text style={s.rowText}>Get {item.tokens} token{item.tokens > 1 ? 's' : ''}</Text>
                </View>

                {/* CTA */}
                <Pressable
                    onPress={() => onSelectOffer?.(item)}
                    style={({ pressed }) => [s.cta, pressed && { opacity: 0.85 }]}
                >
                    <Text style={s.ctaText}>
                    {item.kind === 'ad' ? 'Watch ad' : `$${item.priceUsd?.toFixed(2)}`}
                    </Text>
                </Pressable>
                </View>
            )}
            />
        </View>
      </View>
    </Modal>
  );
}

const s = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.55)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  sheet: {
    width: '100%',
    maxWidth: 560,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
  },
  closeBtn: { position: 'absolute', right: 10, top: 10, zIndex: 10 },
  title: { fontSize: 22, fontWeight: '800', textAlign: 'center', marginTop: 6, marginBottom: 8, color: '#111' },
  subtitle: { fontSize: 16, textAlign: 'center', color: '#222' },
  highlight: { color: '#ff3b6b', fontWeight: '700' },
  caption: { textAlign: 'center', color: '#9aa', marginTop: 4, marginBottom: 12 },
  separator: { height: 12 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fff',
    paddingVertical: 10,
  },
  left: { flexDirection: 'row', alignItems: 'center', flexShrink: 1 },
  rowText: { fontSize: 16, color: '#111' },
  cta: {
    backgroundColor: '#ff2d55',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 10,
    minWidth: 96,
    alignItems: 'center',
  },
  ctaText: { color: '#fff', fontWeight: '700' },
  icon: { width: 28, height: 28, marginRight: 12 },

});

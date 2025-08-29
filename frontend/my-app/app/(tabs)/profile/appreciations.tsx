// app/(tabs)/profile/appreciation.tsx
import { useEffect, useMemo, useState } from 'react';
import {
  FlatList,
  Image,
  StyleSheet,
  Dimensions,
  View,
  ActivityIndicator,
  Alert,
  Pressable,
} from 'react-native';
import TokenAlertBanner from '../../../src/components/TokenAlertBanner';
import PromoCard from '../../../src/components/PromoCard';
import GetMoreTokensModal from '../../../src/components/GetMoreTokensModal';
import { fetchAppreciations, AppreciationItem } from '../../../src/services/appreciationService';
import { fetchRemainingTokens, fetchTokenOffers } from '../../../src/services/tokenService';

const numColumns = 3;
const tileW = Dimensions.get('window').width / numColumns;
const tileH = tileW * 1.5; // your current 2:3-ish aspect

export default function ProfileAppreciationTab() {
  const [data, setData] = useState<AppreciationItem[] | null>(null);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [offers, setOffers] = useState<Awaited<ReturnType<typeof fetchTokenOffers>>>([]);
  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => {
    fetchAppreciations('current-user-id').then(setData);
    fetchRemainingTokens('current-user-id').then(setRemaining);
    fetchTokenOffers().then(setOffers);
  }, []);

  const header = useMemo(
    () => (
      <>
        <View style={s.spacer} />
        <TokenAlertBanner remaining={remaining ?? 0} />
        <View style={s.divider} />
        <PromoCard
          title="Want more tokens?"
          subtitle="Buy or watch ads to get more tokens"
          ctaLabel="Get more"
          onPress={() => setModalVisible(true)}
        />
        <View style={s.gridTopSpacer} />
      </>
    ),
    [remaining]
  );

  if (!data) {
    return (
      <View style={[s.listContent, { flex: 1, justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <>
      <FlatList
        data={data}
        keyExtractor={(item) => item.id}
        numColumns={numColumns}
        ListHeaderComponent={header}
        renderItem={({ item }) => (
          <Pressable
            onPress={() => Alert.alert('Image pressed', `id: ${item.id}`)}
            // onLongPress={() => ...}
            style={({ pressed }) => [
              s.tile,
              pressed && s.tilePressed,
              { width: tileW, height: tileH },
            ]}
          >
            <Image source={{ uri: item.imageUrl }} style={s.image} />
          </Pressable>
        )}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={s.listContent}
      />

      <GetMoreTokensModal
        visible={modalVisible}
        onClose={() => setModalVisible(false)}
        remaining={remaining ?? 0}
        offers={offers}
        onSelectOffer={(offer) => {
          if (offer.kind === 'ad') {
            setModalVisible(false);
            Alert.alert('Watch Ad', `Reward: ${offer.tokens} token${offer.tokens > 1 ? 's' : ''}`);
          } else {
            setModalVisible(false);
            Alert.alert('Checkout', `Purchase ${offer.tokens} tokens for $${offer.priceUsd.toFixed(2)}`);
          }
        }}
      />
    </>
  );
}

const s = StyleSheet.create({
  listContent: { backgroundColor: '#fff' },
  spacer: { height: 8 },
  divider: { height: 1, backgroundColor: '#f3f3f3' },
  gridTopSpacer: { height: 8 },

  tile: {
    overflow: 'hidden',
  },
  tilePressed: {
    opacity: 0.8, // subtle feedback on press
  },
  image: {
    width: '100%',
    height: '100%',
  },
});

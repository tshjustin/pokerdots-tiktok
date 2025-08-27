import { useEffect, useState, useMemo } from 'react';
import {
  FlatList,
  Image,
  StyleSheet,
  Dimensions,
  View,
  Alert,
  ActivityIndicator,
} from 'react-native';
import TokenAlertBanner from '../../../src/components/TokenAlertBanner';
import PromoCard from '../../../src/components/PromoCard';
import { fetchAppreciations, AppreciationItem } from '../../../src/services/appreciationService';

const numColumns = 3;
const size = Dimensions.get('window').width / numColumns;

export default function ProfileAppreciationTab() {
  const [data, setData] = useState<AppreciationItem[] | null>(null);

  useEffect(() => {
    fetchAppreciations('current-user-id').then(setData);
  }, []);

  const header = useMemo(
    () => (
      <>
        <View style={s.spacer} />
        <TokenAlertBanner remaining={46} />
        <View style={s.divider} />
        <PromoCard
          title="Want more tokens?"
          subtitle="Buy or watch ads to get more tokens"
          ctaLabel="Get more"
          onPress={() =>
            Alert.alert('Get more', 'TODO: navigate to purchase/watch flow')
          }
        />
        <View style={s.gridTopSpacer} />
      </>
    ),
    []
  );

  if (!data) {
    return (
      <View style={[s.listContent, { flex: 1, justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <FlatList
      data={data}
      keyExtractor={(item) => item.id}
      numColumns={numColumns}
      ListHeaderComponent={header}
      renderItem={({ item }) => (
        <Image source={{ uri: item.imageUrl }} style={{ width: size, height: size }} />
      )}
      showsVerticalScrollIndicator={false}
      contentContainerStyle={s.listContent}
    />
  );
}

const s = StyleSheet.create({
  listContent: {
    backgroundColor: '#fff',
  },
  spacer: { height: 8 },
  divider: { height: 1, backgroundColor: '#f3f3f3' },
  gridTopSpacer: { height: 8 },
});

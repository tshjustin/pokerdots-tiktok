import { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, FlatList } from 'react-native';
import MetricCard from '../../../src/components/MetricCard';
import InfoModal from '../../../src/components/InfoModal';
import { fetchDashboardMetrics, Metric } from '../../../src/services/dashboardService';

export default function ProfileDashboardTab() {
  const [metrics, setMetrics] = useState<Metric[] | null>(null);
  const [infoOpen, setInfoOpen] = useState(false);

  useEffect(() => {
    fetchDashboardMetrics('current-user-id').then(setMetrics);
  }, []);

  if (!metrics) {
    return (
      <View style={[s.container, { alignItems: 'center', justifyContent: 'center' }]}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <View style={s.container}>
      <Text style={s.sectionSubtitle}>This year</Text>
      <Text style={s.sectionTitle}>Key metrics</Text>

      <FlatList
        data={metrics}
        keyExtractor={(m) => m.id}
        numColumns={2}
        columnWrapperStyle={{ justifyContent: 'space-between' }}
        contentContainerStyle={{ paddingTop: 4 }}
        renderItem={({ item, index }) => (
          <MetricCard
            title={item.title}
            value={item.value}
            subvalue={item.subvalue}
            backgroundColor={item.backgroundColor}
            textColor={item.textColor}
            // show info icon only for the Appreciation card (id === 'appreciation'),
            // or make this configurable from the service.
            showInfo={item.id === 'appreciation'}
            onPressInfo={() => setInfoOpen(true)}
          />
        )}
        showsVerticalScrollIndicator={false}
      />

      <InfoModal
        visible={infoOpen}
        title="Appreciation Value"
        message="This represents the total value of tokens you received this year."
        onClose={() => setInfoOpen(false)}
      />
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#ffffff' },
  sectionTitle: { fontSize: 16, fontWeight: '600', marginBottom: 4 },
  sectionSubtitle: { fontSize: 14, color: '#555', marginBottom: 12 },
});

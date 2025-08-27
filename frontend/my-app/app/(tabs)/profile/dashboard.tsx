import { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, FlatList } from 'react-native';
import MetricCard from '../../../src/components/MetricCard';
import { fetchDashboardMetrics, Metric } from '../../../src/services/dashboardService';
import { Alert } from 'react-native';

export default function ProfileDashboardTab() {
  const [metrics, setMetrics] = useState<Metric[] | null>(null);

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
        renderItem={({ item }) => (
          <MetricCard
            title={item.title}
            value={item.value}
            subvalue={item.subvalue}
            backgroundColor={item.backgroundColor}
            textColor={item.textColor}
            showInfo={item.showInfo}
            onPressInfo={() => {
              if (item.id === 'appreciation') {
                Alert.alert(
                  'Appreciation Value',
                  'This represents the total value of tokens you received this year.'
                );
              }
            }}
          />
        )}
        contentContainerStyle={{ paddingTop: 4 }}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: '#ffffff' },
  sectionTitle: { fontSize: 16, fontWeight: '600', marginBottom: 4 },
  sectionSubtitle: { fontSize: 14, color: '#555', marginBottom: 12 },
});

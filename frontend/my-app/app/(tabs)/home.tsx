import { View, Text, FlatList, Dimensions, StyleSheet } from 'react-native';

const DATA = Array.from({ length: 10 }, (_, i) => ({ id: String(i), title: `Video ${i + 1}` }));
const { height } = Dimensions.get('window');

export default function HomePage() {
  return (
    <FlatList
      data={DATA}
      keyExtractor={(item) => item.id}
      pagingEnabled
      snapToInterval={height}
      decelerationRate="fast"
      renderItem={({ item }) => (
        <View style={[s.page, { height }]}>
          {/* replace with a proper Video component later */}
          <Text style={s.text}>{item.title}</Text>
        </View>
      )}
    />
  );
}

const s = StyleSheet.create({
  page: { justifyContent: 'center', alignItems: 'center', backgroundColor: '#000' },
  text: { color: '#fff', fontSize: 32, fontWeight: '600' }
});

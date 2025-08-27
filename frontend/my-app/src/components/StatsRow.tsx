import { View, StyleSheet } from 'react-native';
import Stat from './Stat';

export type StatItem = { label: string; value: number | string };
type Props = { items: StatItem[] };

export default function StatsRow({ items }: Props) {
  return (
    <View style={s.row}>
      {items.map((it) => (
        <Stat key={it.label} label={it.label} value={it.value} />
      ))}
    </View>
  );
}

const s = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'center' },
});

import { View, Text, StyleSheet } from 'react-native';

type Props = {
  remaining: number;            // e.g. 46
  period?: string;              // e.g. "this month"
  tint?: string;                // accent dot color
};

export default function TokenAlertBanner({ remaining, period = 'this month', tint = '#ff3b6b' }: Props) {
  return (
    <View style={s.container}>
      <View style={[s.dot, { backgroundColor: tint }]} />
      <Text style={s.text}>
        You have <Text style={s.bold}>{remaining}</Text> tokens left to give out {period}
      </Text>
    </View>
  );
}

const s = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
  },
  dot: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: '#ffd3df',
  },
  text: { color: '#333', fontSize: 14 },
  bold: { fontWeight: '700' },
});

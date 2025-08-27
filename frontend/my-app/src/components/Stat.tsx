import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';

type Props = {
  label: string;
  value: number | string;
  containerStyle?: ViewStyle;
  valueStyle?: TextStyle;
  labelStyle?: TextStyle;
};

export default function Stat({ label, value, containerStyle, valueStyle, labelStyle }: Props) {
  return (
    <View style={[s.container, containerStyle]}>
      <Text style={[s.value, valueStyle]}>{value}</Text>
      <Text style={[s.label, labelStyle]}>{label}</Text>
    </View>
  );
}

const s = StyleSheet.create({
  container: { alignItems: 'center', marginHorizontal: 20 },
  value: { fontSize: 16, fontWeight: 'bold' },
  label: { color: '#666', fontSize: 13 },
});

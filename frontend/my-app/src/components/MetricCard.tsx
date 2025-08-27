import { View, Text, StyleSheet, ViewStyle, TextStyle, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export type MetricCardProps = {
  title: string;
  value: string | number;
  subvalue?: string | number;
  backgroundColor?: string;
  textColor?: string;
  containerStyle?: ViewStyle;
  titleStyle?: TextStyle;
  valueStyle?: TextStyle;
  subvalueStyle?: TextStyle;
  showInfo?: boolean;
  onPressInfo?: () => void;
};

export default function MetricCard({
  title,
  value,
  subvalue,
  backgroundColor = '#f5f5f5',
  textColor = '#333',
  containerStyle,
  titleStyle,
  valueStyle,
  subvalueStyle,
  showInfo,
  onPressInfo,
}: MetricCardProps) {
  const isDark = textColor === '#fff' || textColor.toLowerCase() === 'white';

  return (
    <View style={[s.card, { backgroundColor }, containerStyle]}>
      <View style={s.titleRow}>
        <Text style={[s.title, { color: textColor }, titleStyle]}>{title}</Text>
        {showInfo && (
          <Pressable onPress={onPressInfo} hitSlop={8} style={{ marginLeft: 4, top: 0, margin:0, padding:0}} >
            <Ionicons
              name="information-circle-outline"
              size={18}
              color={textColor}
              style={{ marginLeft: 4, lineHeight: 18, top: 0}}
            />
          </Pressable>
        )}
      </View>
      <Text style={[s.value, { color: textColor }, valueStyle]}>{String(value)}</Text>
      {subvalue != null && (
        <Text style={[s.value, { color: textColor }, subvalueStyle]}>
          {String(subvalue)}
        </Text>
      )}
    </View>
  );
}

const s = StyleSheet.create({
  card: {
    flexBasis: '48%',
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
    borderColor: '#eeeeee',
    minHeight: 100,
    justifyContent: 'center',
  },
  titleRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  title: { fontSize: 14, marginBottom: 0 },
  value: { fontSize: 16, fontWeight: '600' },
});

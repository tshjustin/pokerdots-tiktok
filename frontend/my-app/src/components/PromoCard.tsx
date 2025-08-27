import { View, Text, StyleSheet, Pressable } from 'react-native';

type Props = {
  title: string;            // "Want more tokens?"
  subtitle: string;         // "Buy or watch ads to get more tokens"
  ctaLabel?: string;        // "Get more"
  onPress?: () => void;
};

export default function PromoCard({ title, subtitle, ctaLabel = 'Get more', onPress }: Props) {
  return (
    <View style={s.wrapper}>
      <View style={s.left}>
        <Text style={s.title}>{title}</Text>
        <Text style={s.subtitle}>{subtitle}</Text>
      </View>

      <Pressable onPress={onPress} style={({ pressed }) => [s.cta, pressed && { opacity: 0.8 }]}>
        <Text style={s.ctaText}>{ctaLabel}</Text>
      </Pressable>
    </View>
  );
}

const s = StyleSheet.create({
  wrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    backgroundColor: '#fff',
  },
  left: { flexShrink: 1, paddingRight: 12 },
  title: { fontSize: 16, fontWeight: '700', marginBottom: 4, color: '#111' },
  subtitle: { fontSize: 13, color: '#666' },
  cta: {
    backgroundColor: '#ff2d55', // TikTok-ish pink
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
  },
  ctaText: { color: '#fff', fontWeight: '700' },
});

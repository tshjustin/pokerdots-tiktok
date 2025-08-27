import { router } from 'expo-router';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import { useState } from 'react';
import { login } from '../../src/services/authService';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [pwd, setPwd] = useState('');
  const [pending, setPending] = useState(false);

  const onLogin = async () => {
    try {
      if (!email || !pwd) return Alert.alert('Missing fields', 'Email and password are required');
      setPending(true);
      await login(email, pwd);
      router.replace('/(tabs)/home');
    } catch (e: any) {
      Alert.alert('Login failed', e.message ?? String(e));
    } finally {
      setPending(false);
    }
  };

  return (
    <View style={s.container}>
      <Text style={s.title}>Login</Text>
      <TextInput style={s.input} placeholder="Email" autoCapitalize="none" value={email} onChangeText={setEmail} />
      <TextInput style={s.input} placeholder="Password" value={pwd} onChangeText={setPwd} secureTextEntry />
      <Button title={pending ? 'Signing in...' : 'Sign in'} onPress={onLogin} disabled={pending} />
      <Button title="Register" onPress={() => router.push('/(auth)/register')} />
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 16 },
  title: { fontSize: 24, marginBottom: 16 },
  input: { borderWidth: 1, borderColor: '#ccc', padding: 10, marginBottom: 12, borderRadius: 8 }
});

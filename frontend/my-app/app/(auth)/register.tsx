import { router } from 'expo-router';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import { useEffect, useState, useMemo } from 'react';
import { registerUser, seedUsersOnce } from '../../src/services/authService';
import { isValidEmail } from '../../src/utils/validation';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [pwd, setPwd] = useState('');
  const [pending, setPending] = useState(false);
  const [touchedEmail, setTouchedEmail] = useState(false);

  useEffect(() => {
    seedUsersOnce();
  }, []);

  const emailOk = useMemo(() => isValidEmail(email), [email]);
  const canSubmit = emailOk && pwd.length >= 6 && !pending;

  const onRegister = async () => {
    try {
      if (!email || !pwd) return Alert.alert('Missing fields', 'Email and password are required');
      if (!emailOk) return Alert.alert('Invalid email', 'Please enter a valid email address');
      if (pwd.length < 6) return Alert.alert('Weak password', 'Use at least 6 characters');

      setPending(true);
      await registerUser(email, pwd);
      router.replace('/(tabs)/home');
    } catch (e: any) {
      Alert.alert('Registration failed', e.message ?? String(e));
    } finally {
      setPending(false);
    }
  };

  const emailShowError = touchedEmail && email.length > 0 && !emailOk;

  return (
    <View style={s.container}>
      <Text style={s.title}>Register</Text>

      <TextInput
        style={[s.input, emailShowError && s.inputError]}
        placeholder="Email"
        autoCapitalize="none"
        autoCorrect={false}
        keyboardType="email-address"
        textContentType="emailAddress"
        value={email}
        onChangeText={setEmail}
        onBlur={() => setTouchedEmail(true)}
      />
      {emailShowError && <Text style={s.errorText}>Please enter a valid email (e.g. name@example.com)</Text>}

      <TextInput
        style={s.input}
        placeholder="Password (min 6)"
        value={pwd}
        onChangeText={setPwd}
        secureTextEntry
        // ❌ remove this:
        // textContentType="newPassword"
        // ✅ use this instead:
        textContentType="none"
        autoComplete="off"
        />


      <Button title={pending ? 'Creating...' : 'Create account'} onPress={onRegister} disabled={!canSubmit} />
      <Button title="Back to login" onPress={() => router.back()} />
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 16 },
  title: { fontSize: 24, marginBottom: 16 },
  input: { borderWidth: 1, borderColor: '#ccc', padding: 10, marginBottom: 8, borderRadius: 8 },
  inputError: { borderColor: '#e53935' },
  errorText: { color: '#e53935', marginBottom: 8 }
});

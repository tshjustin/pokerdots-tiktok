import AsyncStorage from '@react-native-async-storage/async-storage';
import { isValidEmail } from '../utils/validation';


export type User = {
  email: string;
  password: string; // demo only; don’t store plaintext in real apps
};

const USERS_KEY = 'demo_users';
const SESSION_KEY = 'demo_current_user';

async function readUsers(): Promise<User[]> {
  const raw = await AsyncStorage.getItem(USERS_KEY);
  return raw ? JSON.parse(raw) : [];
}

async function writeUsers(users: User[]) {
  await AsyncStorage.setItem(USERS_KEY, JSON.stringify(users));
}

/** Seed some dummy users once (optional) */
export async function seedUsersOnce() {
  const current = await readUsers();
  if (current.length === 0) {
    await writeUsers([{ email: 'demo@demo.com', password: 'password' }]);
  }
}
export async function registerUser(email: string, password: string) {
  email = email.trim().toLowerCase();
  if (!isValidEmail(email)) throw new Error('Invalid email format');
  const users = await readUsers();
  if (users.some(u => u.email === email)) {
    throw new Error('Email already registered');
  }
  users.push({ email, password });
  await writeUsers(users);
  await AsyncStorage.setItem(SESSION_KEY, JSON.stringify({ email }));
}

export async function login(email: string, password: string) {
  email = email.trim().toLowerCase();
  const users = await readUsers();
  const user = users.find(u => u.email === email && u.password === password);
  if (!user) throw new Error('Invalid email or password');
  await AsyncStorage.setItem(SESSION_KEY, JSON.stringify({ email }));
}

export async function getCurrentUser(): Promise<{ email: string } | null> {
  const raw = await AsyncStorage.getItem(SESSION_KEY);
  return raw ? JSON.parse(raw) : null;
}

export async function logout() {
  await AsyncStorage.removeItem(SESSION_KEY);
}

export async function clearAllDemoData() {
  await AsyncStorage.multiRemove([USERS_KEY, SESSION_KEY]);
}


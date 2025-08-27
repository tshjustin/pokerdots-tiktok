// super-light email check (good enough for apps; not RFC-perfect)
export const isValidEmail = (v: string) =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());

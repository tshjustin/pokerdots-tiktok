export type ProfileSummary = {
  username: string;
  avatarUrl: string;
  following: number;
  followers: number;
  likes: number;
};

// pretend to call an API; replace with real fetch later
export async function fetchProfileSummary(userId: string): Promise<ProfileSummary> {
  // simulate latency
  await new Promise((r) => setTimeout(r, 300));
  return {
    username: '@jacob_w',
    avatarUrl: 'https://i.pravatar.cc/200',
    following: 14,
    followers: 38,
    likes: 91,
  };
}

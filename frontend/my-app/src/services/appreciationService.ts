export type AppreciationItem = { id: string; imageUrl: string };

export async function fetchAppreciations(userId: string): Promise<AppreciationItem[]> {
  // simulate latency
  await new Promise((r) => setTimeout(r, 300));

  return [
    { id: '1', imageUrl: 'https://picsum.photos/400/400?random=1' },
    { id: '2', imageUrl: 'https://picsum.photos/400/400?random=2' },
    { id: '3', imageUrl: 'https://picsum.photos/400/400?random=3' },
    { id: '4', imageUrl: 'https://picsum.photos/400/400?random=4' },
    { id: '5', imageUrl: 'https://picsum.photos/400/400?random=5' },
    { id: '6', imageUrl: 'https://picsum.photos/400/400?random=6' },
    { id: '7', imageUrl: 'https://picsum.photos/400/400?random=7' },
    { id: '8', imageUrl: 'https://picsum.photos/400/400?random=8' },
    { id: '9', imageUrl: 'https://picsum.photos/400/400?random=9' },
  ];
}

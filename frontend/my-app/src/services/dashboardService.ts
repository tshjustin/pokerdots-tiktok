export type Metric = {
  id: string;
  title: string;
  value: string | number;
  subvalue?: string | number;
  backgroundColor?: string;
  textColor?: string;
  showInfo?: boolean;

};

export async function fetchDashboardMetrics(userId: string): Promise<Metric[]> {
  await new Promise((r) => setTimeout(r, 200)); // simulate latency
  return [
    {
        id: 'appreciation',
        title: 'Appreciation Value',
        value: '50 tokens',
        subvalue: '$108.25',
        backgroundColor: '#00bcd4',
        textColor: '#ffffff',
        showInfo: true, // 👈
    },
    { id: 'views', title: 'Video views', value: 205 },
    { id: 'likes', title: 'Likes', value: 125 },
    { id: 'comments', title: 'Comments', value: 1 },
  ]; 

}

import type { TokenOffer } from '../components/GetMoreTokensModal'; // if no alias: '../components/GetMoreTokensModal'

export async function fetchRemainingTokens(userId: string): Promise<number> {
  await new Promise((r) => setTimeout(r, 150));
  return 46;
}

export async function fetchTokenOffers(): Promise<TokenOffer[]> {
  await new Promise((r) => setTimeout(r, 150));
  return [
    { id: 'ad1', tokens: 1, kind: 'ad', icon: require('../../assets/icons/watchad.png') },
    { id: 'p7', tokens: 7, kind: 'purchase', priceUsd: 0.7, icon: require('../../assets/icons/7coins.png') },
    { id: 'p9', tokens: 9, kind: 'purchase', priceUsd: 0.8, icon: require('../../assets/icons/9coins.png') },
    { id: 'p13', tokens: 13, kind: 'purchase', priceUsd: 1.0, icon: require('../../assets/icons/13coins.png') },
  ];
}



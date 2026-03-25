import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Hekate Prime — Türkiye\'nin İlk Mistik AI Kehanet Platformu',
  description: '78 kartlık tarot, astroloji, numeroloji ve Shadow Mode ile kadim bilgeliği yapay zeka ile buluşturan Türkçe kehanet platformu.',
  keywords: 'tarot, astroloji, numeroloji, kehanet, AI tarot, yapay zeka tarot, shadow mode, Hekate, mistik AI, Türkçe tarot',
  openGraph: {
    title: 'Hekate Prime — Mistik AI Kehanet',
    description: 'Türkiye\'nin ilk gerçek AI oracle platformu. 78 kart, Shadow Mode, hafıza sistemi.',
    type: 'website',
    locale: 'tr_TR',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Hekate Prime',
    description: 'Türkiye\'nin ilk mistik AI kehanet platformu.',
  },
  robots: { index: true, follow: true },
  alternates: { canonical: 'https://hekateprime.com' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Crimson+Pro:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet" />
      </head>
      <body>{children}</body>
    </html>
  )
}

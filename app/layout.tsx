import './globals.css';import AppShell from '@/components/AppShell';
export const metadata={title:'Sahakar Sahayak — Multilingual Citizen Assistance',description:'AI-powered multilingual government and cooperative assistance platform'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><AppShell>{children}</AppShell></body></html>}

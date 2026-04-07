import "./globals.css";

export const metadata = {
  title: "MUFC Fighter Builder",
  description: "Create fighters for the MUFC AI vs AI league."
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

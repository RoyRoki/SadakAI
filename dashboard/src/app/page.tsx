import dynamic from "next/dynamic";

const HazardMap = dynamic(() => import("@/components/map/HazardMap"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full">
      <div className="text-muted-foreground">Loading map...</div>
    </div>
  ),
});

export default function HomePage() {
  return (
    <div className="h-full">
      <HazardMap />
    </div>
  );
}

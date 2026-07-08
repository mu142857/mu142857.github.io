export const THEMES = {
  rustCity: {
    layers: [
      { src: 'Assets/rust_city_style/0.0background.png', factor: 0.0 },
      { src: 'Assets/rust_city_style/0.2background.png', factor: 0.2 },
      { src: 'Assets/rust_city_style/0.4background.png', factor: 0.4 },
      // Natively 160x80 (10px short) — bottom-aligned so its ground line matches
      // the other layers, based on its pole art running to its frame's bottom edge.
      { src: 'Assets/rust_city_style/0.6background.png', factor: 0.6, align: 'bottom' },
      { src: 'Assets/rust_city_style/0.8background.png', factor: 0.8 },
    ],
    ground: { src: 'Assets/rust_city_style/rust_city_ground.png', factor: 1.0 },
    // Street lamp placed between adjacent buildings (also emits a warm glow).
    lamp: 'Assets/rust_city_style/rust_city_light.png',
    // One building image per section, index-aligned to the BUILDINGS array order.
    buildings: [
      'Assets/rust_city_style/building1.png',
      'Assets/rust_city_style/building2.png',
      'Assets/rust_city_style/building3.png',
      'Assets/rust_city_style/building4.png',
      'Assets/rust_city_style/building5.png',
      'Assets/rust_city_style/building6.png',
    ],
  },
  // Reserved: a second theme is a pure data addition here, nothing else changes.
  forestTown: null,
};

// Building section mapping, in the order the visitor meets them walking right from spawn.
// The MOST important sections come first (games / projects / music — what hackathons & events
// care about), then the resume-style sections. worldX and width are assigned at runtime by
// World.setTheme, which packs the buildings left-to-right with a lamp between each pair.
// NOTE: the building ART (themes.js `buildings` array) is index-aligned to THIS array, so the
// first entry uses building1.png, the second building2.png, etc. Reordering here just moves
// which section sits behind each building; it does not need matching art changes.
export const BUILDINGS = [
  { id: 'gameProjects', sectionId: 'gameProjects', label: 'Game Projects' },
  { id: 'projects', sectionId: 'projects', label: 'Projects' },
  { id: 'music', sectionId: 'music', label: 'Music Composing' },
  { id: 'about', sectionId: 'about', label: 'About Me' },
  { id: 'skills', sectionId: 'skills', label: 'Technical Skills' },
  { id: 'experience', sectionId: 'experience', label: 'Work Experience' },
];

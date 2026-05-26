// Script pour générer les icônes SVG → PNG
// Lance avec : node generate_icons.js
const sharp = require('sharp')
const fs    = require('fs')
const path  = require('path')

const sizes = [72, 96, 128, 144, 192, 512]

const svgIcon = (size) => Buffer.from(`
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}"
  xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0A0F1E"/>
      <stop offset="100%" stop-color="#111D35"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00D4FF"/>
      <stop offset="100%" stop-color="#7B2FFF"/>
    </linearGradient>
  </defs>
  <rect width="${size}" height="${size}" rx="${Math.round(size*0.22)}" fill="#0A0F1E"/>
  <rect width="${size}" height="${size}" rx="${Math.round(size*0.22)}"
    fill="none" stroke="#00D4FF" stroke-width="${Math.round(size*0.03)}"
    opacity="0.5"/>
  <rect x="${Math.round(size*0.38)}" y="${Math.round(size*0.18)}"
    width="${Math.round(size*0.24)}" height="${Math.round(size*0.64)}"
    rx="${Math.round(size*0.05)}" fill="#00D4FF"/>
  <rect x="${Math.round(size*0.18)}" y="${Math.round(size*0.38)}"
    width="${Math.round(size*0.64)}" height="${Math.round(size*0.24)}"
    rx="${Math.round(size*0.05)}" fill="#00D4FF"/>
  <circle cx="${Math.round(size*0.5)}" cy="${Math.round(size*0.5)}"
    r="${Math.round(size*0.09)}" fill="#0A0F1E"/>
  <circle cx="${Math.round(size*0.5)}" cy="${Math.round(size*0.5)}"
    r="${Math.round(size*0.05)}" fill="#7B2FFF"/>
</svg>
`)

const outDir = path.join(__dirname)

async function generate() {
  console.log('🧬 Génération des icônes ResistIA PNG...\n')

  for (const size of sizes) {
    const outPath = path.join(outDir, `icon-${size}.png`)
    try {
      await sharp(svgIcon(size))
        .resize(size, size)
        .png({ quality: 100, compressionLevel: 9 })
        .toFile(outPath)
      console.log(`✅ icon-${size}.png — ${size}x${size}px`)
    } catch (err) {
      console.error(`❌ Erreur icon-${size}:`, err.message)
    }
  }

  // Icône spéciale maskable (fond plein pour Android)
  const maskableSvg = (size) => Buffer.from(`
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}"
      xmlns="http://www.w3.org/2000/svg">
      <rect width="${size}" height="${size}" fill="#0A0F1E"/>
      <rect x="${Math.round(size*0.35)}" y="${Math.round(size*0.15)}"
        width="${Math.round(size*0.30)}" height="${Math.round(size*0.70)}"
        rx="${Math.round(size*0.05)}" fill="#00D4FF"/>
      <rect x="${Math.round(size*0.15)}" y="${Math.round(size*0.35)}"
        width="${Math.round(size*0.70)}" height="${Math.round(size*0.30)}"
        rx="${Math.round(size*0.05)}" fill="#00D4FF"/>
      <circle cx="${Math.round(size*0.5)}" cy="${Math.round(size*0.5)}"
        r="${Math.round(size*0.09)}" fill="#0A0F1E"/>
      <circle cx="${Math.round(size*0.5)}" cy="${Math.round(size*0.5)}"
        r="${Math.round(size*0.05)}" fill="#7B2FFF"/>
    </svg>
  `)

  for (const size of [192, 512]) {
    const outPath = path.join(outDir, `icon-${size}-maskable.png`)
    try {
      await sharp(maskableSvg(size))
        .resize(size, size)
        .png({ quality: 100 })
        .toFile(outPath)
      console.log(`✅ icon-${size}-maskable.png`)
    } catch (err) {
      console.error(`❌ Erreur maskable ${size}:`, err.message)
    }
  }

  console.log('\n✅ Toutes les icônes PNG générées dans public/icons/')
}

generate()
/**
 * PostFX — the cinematic post-processing stack that gives the scene its
 * "AAA" finish: screen-space ambient occlusion (grounds every object and
 * deepens crevices), subtle bloom on emissives, a gentle color grade,
 * vignette, and ACES filmic tone-mapping as the final output transform.
 *
 * The renderer's own tone-mapping is disabled (NoToneMapping on the Canvas gl)
 * so the ToneMapping effect here is the single, correct HDR→display transform.
 */
import {
  EffectComposer,
  N8AO,
  Bloom,
  HueSaturation,
  BrightnessContrast,
  Vignette,
  ToneMapping,
} from '@react-three/postprocessing';
import { ToneMappingMode } from 'postprocessing';

export default function PostFX() {
  return (
    <EffectComposer multisampling={4} enableNormalPass={false}>
      {/* Ambient occlusion — contact shadows in crevices & under equipment.
          World-space radius tuned to the mine's scale (facilities ~10–28u). */}
      <N8AO
        halfRes
        color="black"
        aoRadius={22}
        distanceFalloff={1.2}
        intensity={2.6}
        aoSamples={16}
        denoiseSamples={8}
        denoiseRadius={12}
        screenSpaceRadius={false}
      />
      {/* Soft glow on bright/emissive elements only (high threshold). */}
      <Bloom
        mipmapBlur
        luminanceThreshold={0.9}
        luminanceSmoothing={0.25}
        intensity={0.5}
        radius={0.7}
      />
      {/* Light color grade — a touch more saturation & contrast = premium look. */}
      <HueSaturation saturation={0.04} />
      <BrightnessContrast brightness={0.01} contrast={0.1} />
      {/* Subtle lens vignette to draw the eye toward the operation. */}
      <Vignette offset={0.2} darkness={0.5} />
      {/* Final filmic transform. */}
      <ToneMapping mode={ToneMappingMode.ACES_FILMIC} />
    </EffectComposer>
  );
}

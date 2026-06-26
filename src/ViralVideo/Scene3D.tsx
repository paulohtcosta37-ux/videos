import React, { useMemo } from 'react';
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import * as THREE from 'three';

// --- CORAÇÃO 3D PULSANTE (CENA 5 - CHOQUE NO PEITO) ---
const PulsingHeart: React.FC = () => {
  const frame = useCurrentFrame();

  // Desenha a forma 2D geométrica do coração usando curvas Bézier
  const heartShape = useMemo(() => {
    const shape = new THREE.Shape();
    shape.moveTo(0, -0.6);
    shape.bezierCurveTo(-0.8, -0.1, -1.2, 0.5, -0.6, 1.1);
    shape.bezierCurveTo(-0.1, 1.6, 0.4, 1.2, 0, 0.7);
    shape.bezierCurveTo(-0.4, 1.2, -0.1, 1.6, 0.6, 1.1);
    shape.bezierCurveTo(1.2, 0.5, 0.8, -0.1, 0, -0.6);
    return shape;
  }, []);

  // Extrusão 3D para dar espessura e relevo ao coração
  const extrudeSettings = useMemo(() => ({
    depth: 0.35,
    bevelEnabled: true,
    bevelSegments: 5,
    steps: 2,
    bevelSize: 0.08,
    bevelThickness: 0.08,
  }), []);

  // Pulsação elástica (batimento duplo característico do coração humano)
  const pulse = interpolate(
    Math.max(0, Math.sin(frame * 0.16) * 0.7 + Math.sin(frame * 0.32) * 0.3),
    [0, 1],
    [1.0, 1.25]
  );

  // Rotação lenta no eixo Y
  const rotationY = frame * 0.025;

  return (
    <mesh 
      scale={[pulse, pulse, pulse]} 
      rotation={[0, rotationY, Math.PI]} // Invertido em 180° para alinhar com o topo
      position={[0, 0.2, 0]}
    >
      <extrudeGeometry args={[heartShape, extrudeSettings]} />
      <meshStandardMaterial 
        color="#ff1a40" 
        roughness={0.2} 
        metalness={0.3} 
        emissive="#3a0008"
      />
    </mesh>
  );
};

// --- PORTAL 3D DE PARTÍCULAS (CENA 6 - DESMAIO / CHOQUE TÉRMICO) ---
const ParticlePortal: React.FC = () => {
  const frame = useCurrentFrame();
  const count = 1500; // Quantidade de pontos de luz

  // Inicializa posições e cores na espiral
  const [positions, colors] = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    let seed = 12345;

    const random = () => {
      seed = (seed * 1664525 + 1013904223) % 4294967296;
      return seed / 4294967296;
    };

    for (let i = 0; i < count; i++) {
      const progress = i / count;
      const angle = progress * Math.PI * 30; // Muitas espirais
      const radius = progress * 3.5;         // Afastando do centro
      
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;
      const z = (random() - 0.5) * 0.6; // Profundidade das partículas

      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;

      // Mistura de cor: azul elétrico (gelo) ao centro ao ciano e roxo nas bordas
      colors[i * 3] = 0.1 + progress * 0.6;     // Vermelho
      colors[i * 3 + 1] = 0.5 - progress * 0.4; // Verde
      colors[i * 3 + 2] = 0.9 - progress * 0.2; // Azul
    }
    return [positions, colors];
  }, []);

  // Rotação em espiral com base no tempo
  const rotationZ = frame * 0.035;

  return (
    <points rotation={[0, 0, rotationZ]}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-color"
          args={[colors, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.065}
        vertexColors
        transparent
        opacity={0.85}
        sizeAttenuation
      />
    </points>
  );
};

// --- CANVAS DE RENDERIZAÇÃO DO REMOTION ---
export const VideoScene3D: React.FC<{ mode: "heart" | "portal" }> = ({ mode }) => {
  const { width, height } = useVideoConfig();

  return (
    <div style={{ flex: 1, backgroundColor: '#090a0f', width: '100%', height: '100%' }}>
      <ThreeCanvas
        width={width}
        height={height}
        camera={{ position: [0, 0, 5], fov: 60 }}
      >
        {/* Configurações de Luz */}
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1.5} />
        <directionalLight position={[-5, 5, 5]} intensity={0.8} />

        {/* Escolha do elemento 3D a renderizar */}
        {mode === "heart" ? <PulsingHeart /> : <ParticlePortal />}
      </ThreeCanvas>
    </div>
  );
};

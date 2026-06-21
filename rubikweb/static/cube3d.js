import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { COLORS, state, updateStatus } from './globals.js';

export const cubes = [];
export let scene, camera, renderer, controls;

const cubeSize = 0.96;
const gap = 0.04;

export function initCube3D(canvasId) {
    const canvas = document.getElementById(canvasId);
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a2a);

    camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
    camera.position.set(3, 2, 5);
    camera.lookAt(0, 0, 0);

    renderer = new THREE.WebGLRenderer({ canvas, alpha: false });
    renderer.setSize(500, 500);
    renderer.setPixelRatio(window.devicePixelRatio);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.autoRotate = false;
    controls.enableZoom = true;
    controls.zoomSpeed = 1.0;
    controls.rotateSpeed = 1.5;

    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 1);
    dirLight.position.set(1, 2, 1);
    scene.add(dirLight);
    const backLight = new THREE.DirectionalLight(0xffffff, 0.5);
    backLight.position.set(-1, -1, -1);
    scene.add(backLight);

    for (let x = -1; x <= 1; x++) {
        for (let y = -1; y <= 1; y++) {
            for (let z = -1; z <= 1; z++) {
                if (Math.abs(x) + Math.abs(y) + Math.abs(z) > 0) {
                    const geometry = new THREE.BoxGeometry(cubeSize, cubeSize, cubeSize);
                    const materials = [];
                    
                    let idxR = 9 + (1 - y) * 3 + (1 - z);
                    if (x === 1) materials.push(new THREE.MeshStandardMaterial({ color: COLORS['R'], roughness: 0.3, metalness: 0.1, name: `facelet_${idxR}` }));
                    else materials.push(new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.5 }));
                    
                    let idxL = 36 + (1 - y) * 3 + (z + 1);
                    if (x === -1) materials.push(new THREE.MeshStandardMaterial({ color: COLORS['L'], roughness: 0.3, metalness: 0.1, name: `facelet_${idxL}` }));
                    else materials.push(new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.5 }));
                    
                    let idxU = (z + 1) * 3 + (x + 1);
                    if (y === 1) materials.push(new THREE.MeshStandardMaterial({ color: COLORS['U'], roughness: 0.3, metalness: 0.1, name: `facelet_${idxU}` }));
                    else materials.push(new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.5 }));
                    
                    let idxD = 27 + (1 - z) * 3 + (x + 1);
                    if (y === -1) materials.push(new THREE.MeshStandardMaterial({ color: COLORS['D'], roughness: 0.3, metalness: 0.1, name: `facelet_${idxD}` }));
                    else materials.push(new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.5 }));
                    
                    let idxF = 18 + (1 - y) * 3 + (x + 1);
                    if (z === 1) materials.push(new THREE.MeshStandardMaterial({ color: COLORS['F'], roughness: 0.3, metalness: 0.1, name: `facelet_${idxF}` }));
                    else materials.push(new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.5 }));
                    
                    let idxB = 45 + (1 - y) * 3 + (1 - x);
                    if (z === -1) materials.push(new THREE.MeshStandardMaterial({ color: COLORS['B'], roughness: 0.3, metalness: 0.1, name: `facelet_${idxB}` }));
                    else materials.push(new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.5 }));
                    
                    const mesh = new THREE.Mesh(geometry, materials);
                    mesh.position.set(x * (cubeSize + gap), y * (cubeSize + gap), z * (cubeSize + gap));
                    scene.add(mesh);
                    
                    cubes.push({ 
                        mesh, 
                        currentPos: { x, y, z },
                        solvedPos: mesh.position.clone(),
                        solvedRot: mesh.rotation.clone()
                    });
                }
            }
        }
    }

    animate();
    
    window.addEventListener('resize', handleResize);
    setTimeout(handleResize, 100);
}

function animate() {
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
}

function handleResize() {
    const container = document.querySelector('.cube-container');
    if (container) {
        const size = container.clientWidth;
        renderer.setSize(size, size);
        camera.aspect = 1;
        camera.updateProjectionMatrix();
    }
}

export function rotateLayer(layer, axis, angle) {
    const pivot = new THREE.Group();
    scene.add(pivot);

    const activeCubes = [];
    const angleRad = angle * Math.PI / 2;
    
    cubes.forEach(cube => {
        let inLayer = false;
        if (axis === 'x' && cube.currentPos.x === layer) inLayer = true;
        if (axis === 'y' && cube.currentPos.y === layer) inLayer = true;
        if (axis === 'z' && cube.currentPos.z === layer) inLayer = true;
        
        if (inLayer) {
            activeCubes.push(cube);
            pivot.attach(cube.mesh);
        }
    });
    
    return new Promise((resolve) => {
        const duration = 150;
        const startTime = performance.now();
        
        function animateRotation(currentTime) {
            const elapsed = currentTime - startTime;
            const t = Math.min(1, elapsed / duration);
            const currentAngle = angleRad * t;
            
            pivot.rotation[axis] = currentAngle;
            
            if (t < 1) {
                requestAnimationFrame(animateRotation);
            } else {
                pivot.rotation[axis] = angleRad;
                pivot.updateMatrixWorld();
                
                activeCubes.forEach(cube => {
                    scene.attach(cube.mesh);
                    cube.currentPos = {
                        x: Math.round(cube.mesh.position.x),
                        y: Math.round(cube.mesh.position.y),
                        z: Math.round(cube.mesh.position.z)
                    };
                    cube.mesh.position.set(
                        cube.currentPos.x,
                        cube.currentPos.y,
                        cube.currentPos.z
                    );
                });
                
                scene.remove(pivot);
                resolve();
            }
        }
        
        requestAnimationFrame(animateRotation);
    });
}

export async function applyMoves(moves) {
    for (const move of moves) {
        let layer, axis, angle;
        const base = move[0];
        const suffix = move[1];
        
        switch(base) {
            case 'U': layer = 1; axis = 'y'; angle = suffix === "'" ? 1 : (suffix === '2' ? -2 : -1); break;
            case 'D': layer = -1; axis = 'y'; angle = suffix === "'" ? -1 : (suffix === '2' ? 2 : 1); break;
            case 'R': layer = 1; axis = 'x'; angle = suffix === "'" ? 1 : (suffix === '2' ? -2 : -1); break;
            case 'L': layer = -1; axis = 'x'; angle = suffix === "'" ? -1 : (suffix === '2' ? 2 : 1); break;
            case 'F': layer = 1; axis = 'z'; angle = suffix === "'" ? 1 : (suffix === '2' ? -2 : -1); break;
            case 'B': layer = -1; axis = 'z'; angle = suffix === "'" ? -1 : (suffix === '2' ? 2 : 1); break;
            default: continue;
        }
        
        const times = Math.abs(angle);
        const dir = Math.sign(angle);
        for (let i = 0; i < times; i++) {
            await rotateLayer(layer, axis, dir);
        }
    }
}

export function resetCube() {
    cubes.forEach(cube => {
        cube.mesh.position.copy(cube.solvedPos);
        cube.mesh.rotation.copy(cube.solvedRot);
        
        cube.currentPos = {
            x: Math.round(cube.solvedPos.x),
            y: Math.round(cube.solvedPos.y),
            z: Math.round(cube.solvedPos.z)
        };
        
        cube.mesh.material.forEach((mat) => {
            if (mat.name && mat.name.startsWith('facelet_')) {
                const idx = parseInt(mat.name.split('_')[1]);
                if (idx < 9) mat.color.setHex(COLORS['U']);
                else if (idx < 18) mat.color.setHex(COLORS['R']);
                else if (idx < 27) mat.color.setHex(COLORS['F']);
                else if (idx < 36) mat.color.setHex(COLORS['D']);
                else if (idx < 45) mat.color.setHex(COLORS['L']);
                else if (idx < 54) mat.color.setHex(COLORS['B']);
            }
        });
    });
    
    state.isCubeScrambled = false;
    updateStatus('Ready', '');
}

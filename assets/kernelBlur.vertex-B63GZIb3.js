import{S as e}from"./QueenCombBabylon-DsB9jNgc.js";import{k as i}from"./kernelBlurVaryingDeclaration-BpBWW5fz.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-FX-lN93C.js";import"./index-Xm2cTeAI.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const n="kernelBlurVertex",t="sampleCoord{X}=sampleCenter+delta*KERNEL_OFFSET{X};";e.IncludesShadersStore[n]||(e.IncludesShadersStore[n]=t);const d={name:n,shader:t},o="kernelBlurVertexShader",a=`attribute vec2 position;uniform vec2 delta;varying vec2 sampleCenter;
#include<kernelBlurVaryingDeclaration>[0..varyingCount]
const vec2 madd=vec2(0.5,0.5);
#define CUSTOM_VERTEX_DEFINITIONS
void main(void) {
#define CUSTOM_VERTEX_MAIN_BEGIN
sampleCenter=(position*madd+madd);
#include<kernelBlurVertex>[0..varyingCount]
gl_Position=vec4(position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;e.ShadersStore[o]||(e.ShadersStore[o]=a);const s=[i,d];for(const r of s)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const f={name:o,shader:a};export{f as kernelBlurVertexShader};

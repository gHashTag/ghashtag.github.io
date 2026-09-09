import{ar as o}from"./ray-nqp9MIGV.js";import"./react-BikoVsHo.js";import"./QueenUniverse-ySrqazwA.js";import"./index-BZfTeQdo.js";import"./motion-DmZWFm6O.js";import"./router-CAi4bOxy.js";import"./specCatalog-ONQ2RJG4.js";const e="glowMapMergeVertexShader",r=`attribute vec2 position;varying vec2 vUV;const vec2 madd=vec2(0.5,0.5);
#define CUSTOM_VERTEX_DEFINITIONS
void main(void) {
#define CUSTOM_VERTEX_MAIN_BEGIN
vUV=position*madd+madd;gl_Position=vec4(position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;o.ShadersStore[e]||(o.ShadersStore[e]=r);const s={name:e,shader:r};export{s as glowMapMergeVertexShader};

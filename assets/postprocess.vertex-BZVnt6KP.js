import{ar as o}from"./ray-nqp9MIGV.js";import"./react-BikoVsHo.js";import"./QueenUniverse-ySrqazwA.js";import"./index-BZfTeQdo.js";import"./motion-DmZWFm6O.js";import"./router-CAi4bOxy.js";import"./specCatalog-ONQ2RJG4.js";const e="postprocessVertexShader",r=`attribute vec2 position;uniform vec2 scale;varying vec2 vUV;const vec2 madd=vec2(0.5,0.5);
#define CUSTOM_VERTEX_DEFINITIONS
void main(void) {
#define CUSTOM_VERTEX_MAIN_BEGIN
vUV=(position*madd+madd)*scale;gl_Position=vec4(position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;o.ShadersStore[e]||(o.ShadersStore[e]=r);const c={name:e,shader:r};export{c as postprocessVertexShader};

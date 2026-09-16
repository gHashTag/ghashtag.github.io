import{ar as o}from"./QueenComb-DojR2dWW.js";import"./index-3zHDZIRR.js";import"./react-D-uFLJMr.js";import"./motion-mybjp1Q4.js";import"./router-4H5ws2tv.js";import"./queenRepositoryWorld-CyuPyfZ9.js";const e="postprocessVertexShader",r=`attribute vec2 position;uniform vec2 scale;varying vec2 vUV;const vec2 madd=vec2(0.5,0.5);
#define CUSTOM_VERTEX_DEFINITIONS
void main(void) {
#define CUSTOM_VERTEX_MAIN_BEGIN
vUV=(position*madd+madd)*scale;gl_Position=vec4(position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;o.ShadersStore[e]||(o.ShadersStore[e]=r);const c={name:e,shader:r};export{c as postprocessVertexShader};

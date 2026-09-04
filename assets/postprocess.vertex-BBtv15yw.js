import{S as o}from"./QueenCombBabylon-Ch90MSLm.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-CFJEwTqY.js";import"./index-DHAlv9Zs.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const e="postprocessVertexShader",t=`attribute vec2 position;uniform vec2 scale;varying vec2 vUV;const vec2 madd=vec2(0.5,0.5);
#define CUSTOM_VERTEX_DEFINITIONS
void main(void) {
#define CUSTOM_VERTEX_MAIN_BEGIN
vUV=(position*madd+madd)*scale;gl_Position=vec4(position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;o.ShadersStore[e]||(o.ShadersStore[e]=t);const c={name:e,shader:t};export{c as postprocessVertexShader};

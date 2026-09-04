import{S as o}from"./QueenCombBabylon-CfZ2XGau.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-BpVVE5sQ.js";import"./index-CEfZVCAR.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const e="glowMapMergeVertexShader",i=`attribute vec2 position;varying vec2 vUV;const vec2 madd=vec2(0.5,0.5);
#define CUSTOM_VERTEX_DEFINITIONS
void main(void) {
#define CUSTOM_VERTEX_MAIN_BEGIN
vUV=position*madd+madd;gl_Position=vec4(position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;o.ShadersStore[e]||(o.ShadersStore[e]=i);const S={name:e,shader:i};export{S as glowMapMergeVertexShader};

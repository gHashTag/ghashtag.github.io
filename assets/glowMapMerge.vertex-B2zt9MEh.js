import{ar as o}from"./QueenComb-CsIJP-oJ.js";import"./index-C-AsBuAC.js";import"./react--6nd5XBq.js";import"./motion-CvAcPNoJ.js";import"./router-CmS70aoX.js";const e="glowMapMergeVertexShader",r=`attribute vec2 position;varying vec2 vUV;const vec2 madd=vec2(0.5,0.5);
#define CUSTOM_VERTEX_DEFINITIONS
void main(void) {
#define CUSTOM_VERTEX_MAIN_BEGIN
vUV=position*madd+madd;gl_Position=vec4(position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;o.ShadersStore[e]||(o.ShadersStore[e]=r);const s={name:e,shader:r};export{s as glowMapMergeVertexShader};

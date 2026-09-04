import{S as i}from"./QueenCombBabylon-Ccpv0aSp.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-kFVbQ4B_.js";import"./index-DjsccCAJ.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const o="proceduralVertexShader",e=`attribute vec2 position;varying vec2 vPosition;varying vec2 vUV;const vec2 madd=vec2(0.5,0.5);
#define CUSTOM_VERTEX_DEFINITIONS
void main(void) {
#define CUSTOM_VERTEX_MAIN_BEGIN
vPosition=position;vUV=position*madd+madd;gl_Position=vec4(position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;i.ShadersStore[o]||(i.ShadersStore[o]=e);const v={name:o,shader:e};export{v as proceduralVertexShader};

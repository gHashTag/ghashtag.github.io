import{S as e}from"./QueenCombBabylon-CfZ2XGau.js";import{h as i}from"./helperFunctions-B46K2oY7.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-BpVVE5sQ.js";import"./index-CEfZVCAR.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const o="rgbdDecodePixelShader",t=`varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=vec4(fromRGBD(texture2D(textureSampler,vUV)),1.0);}`;e.ShadersStore[o]||(e.ShadersStore[o]=t);const n=[i];for(const r of n)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const h={name:o,shader:t};export{h as rgbdDecodePixelShader};

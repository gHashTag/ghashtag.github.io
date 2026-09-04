import{S as e}from"./QueenCombBabylon-DOdGX8_Q.js";import{h as i}from"./helperFunctions-SD2qWj7z.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-DB_P-JXd.js";import"./index--wm36luZ.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const o="rgbdEncodePixelShader",t=`varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=toRGBD(texture2D(textureSampler,vUV).rgb);}`;e.ShadersStore[o]||(e.ShadersStore[o]=t);const n=[i];for(const r of n)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const h={name:o,shader:t};export{h as rgbdEncodePixelShader};

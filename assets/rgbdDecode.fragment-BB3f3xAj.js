import{a$ as e}from"./QueenComb-BDBFoqh7.js";import{h as a}from"./helperFunctions-Cfoi0kpb.js";import"./index-Is5pOJIg.js";import"./react--6nd5XBq.js";import"./motion-CvAcPNoJ.js";import"./router-DxTwtRHr.js";const o="rgbdDecodePixelShader",t=`varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=vec4(fromRGBD(texture2D(textureSampler,vUV)),1.0);}`;e.ShadersStore[o]||(e.ShadersStore[o]=t);const i=[a];for(const r of i)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const l={name:o,shader:t};export{l as rgbdDecodePixelShader};

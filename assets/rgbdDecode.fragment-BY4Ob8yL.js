import{a$ as e}from"./QueenComb-CBdTszha.js";import{h as a}from"./helperFunctions-BToISBCA.js";import"./index-Bg02ixgT.js";import"./react--6nd5XBq.js";import"./motion-CvAcPNoJ.js";import"./router-DxTwtRHr.js";const o="rgbdDecodePixelShader",t=`varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=vec4(fromRGBD(texture2D(textureSampler,vUV)),1.0);}`;e.ShadersStore[o]||(e.ShadersStore[o]=t);const i=[a];for(const r of i)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const l={name:o,shader:t};export{l as rgbdDecodePixelShader};

import{bG as e}from"./Queen-DvYDZ44X.js";import{h as n}from"./helperFunctions-TEigTV5e.js";import"./index-oUrwI138.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const o="rgbdEncodePixelShader",t=`varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=toRGBD(texture2D(textureSampler,vUV).rgb);}`;e.ShadersStore[o]||(e.ShadersStore[o]=t);const i=[n];for(const r of i)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const l={name:o,shader:t};export{l as rgbdEncodePixelShader};

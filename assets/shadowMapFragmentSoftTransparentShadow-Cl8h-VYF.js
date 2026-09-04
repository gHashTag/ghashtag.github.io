import{bF as a}from"./Queen-BoQ2Mniu.js";import"./index-BI3gVyoO.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const r="shadowMapFragmentSoftTransparentShadow",o=`#if SM_SOFTTRANSPARENTSHADOW==1
if ((bayerDither8(floor(((fragmentInputs.position.xy)%(8.0)))))/64.0>=uniforms.softTransparentShadowSM.x*alpha) {discard;}
#endif
`;a.IncludesShadersStoreWGSL[r]||(a.IncludesShadersStoreWGSL[r]=o);const d={name:r,shader:o};export{d as shadowMapFragmentSoftTransparentShadowWGSL};

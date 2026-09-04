import{bG as a}from"./Queen-DeLaiO_C.js";import"./index-Q5Yg1fgD.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const r="shadowMapFragmentSoftTransparentShadow",o=`#if SM_SOFTTRANSPARENTSHADOW==1
if ((bayerDither8(floor(mod(gl_FragCoord.xy,8.0))))/64.0>=softTransparentShadowSM.x*alpha) discard;
#endif
`;a.IncludesShadersStore[r]||(a.IncludesShadersStore[r]=o);const n={name:r,shader:o};export{n as shadowMapFragmentSoftTransparentShadow};

// Copyright (C) 2023 Percent Human LLC


import iconLogo from "data-base64:~assets/icon.png"
import cssTooltip from "data-text:react-tooltip/dist/react-tooltip.css"
import cssText from "data-text:~contents/FullDoc.css"
import cssBaseText from "data-text:~base.css"
import type { PlasmoCSConfig, PlasmoGetInlineAnchor } from "plasmo"
import { Tooltip } from "react-tooltip"
import "@plasmohq/messaging/background"

import { sendToBackground } from "@plasmohq/messaging"

export const getStyle = () => {
  const style = document.createElement("style")
  style.textContent = cssBaseText+ cssText + cssTooltip
  return style
}

export const config: PlasmoCSConfig = {
  matches: ["https://docs.google.com/document/*"]
}
export const getInlineAnchor: PlasmoGetInlineAnchor = async () =>
  document.querySelector("#docs-presence-container")
export const getShadowHostId = () => "percent-human-fulldoc"

const PercentHumanFullDoc = () => {
  async function handleClick() {
    console.log("Percent Human: Title called")
    // chrome.runtime.sendMessage({ message: "initiateSidebar" })
    const resp = await sendToBackground({
      name: "initiateSidebar",
      body:{
        content: "random document text that is plagiarised"
      }
    })
    console.log(resp)
    // chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    //   var tabId = tabs[0].id;
    //   chrome.tabs.sendMessage(tabId, {message: "showSidebar"});
    // });
  }

  return (
    <>
      <button
        id="percent-human-fulldoc"
        onClick={handleClick}
        className="flex justify-center items-center text-lg font-semibold hover:bg-gdocs_bar_gray rounded-3xl px-4 py-2 bg-white hover:underline mr-2">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth="1.2"
          stroke="currentColor"
          className="w-3 h-3 lg:hidden text-gray-800 self-end mr-1">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"
          />
        </svg>

        <img className="h-5 w-5 lg:mr-2" src={iconLogo} alt="logo" />
        <span className="hidden lg:block font-bold text-gray-800 font-sans tracking-normal">Authenticity</span>
      </button>
      <Tooltip
        anchorId="percent-human-fulldoc"
        place="bottom"
        content="View document authenticity"
        clickable={true}
        variant="dark"
        className="percent-human-fulldoc-tooltip"
        offset={6}
        id="percent-human-fulldoc-tooltip"
      />
    </>
  )
}

export default PercentHumanFullDoc

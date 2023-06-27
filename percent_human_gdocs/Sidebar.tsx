// Copyright (C) 2023 Percent Human LLC
//! Work in progress

import { ArcElement, Chart as ChartJS, Legend, Tooltip } from "chart.js"
import DoughnutLabel from "chartjs-plugin-doughnutlabel-rebourne"
import iconLogo from "data-base64:~assets/icon.png"
import cssBaseText from "data-text:~base.css"
import cssText from "data-text:~contents/Sidebar.css"
import type { PlasmoCSConfig, PlasmoGetOverlayAnchor } from "plasmo"
import { useEffect, useState } from "react"
import { Doughnut } from "react-chartjs-2"
import { DocsEditHistory, PercentHumanScores} from "~ph_gdocs/utils/"

ChartJS.register(ArcElement, Tooltip, Legend, DoughnutLabel)

export const config: PlasmoCSConfig = {
  matches: ["https://docs.google.com/document/*"]
}
export const getOverlayAnchor: PlasmoGetOverlayAnchor = async () =>
  document.querySelector(".companion-shell")

export const getStyle = () => {
  const style = document.createElement("style")
  style.textContent = cssBaseText + cssText
  return style
}

export const getShadowHostId = () => "percent-human-sidebar"

const AnalysisSidebar = () => {
  const [showSidebar, setShowSidebar] = useState(false)
  const [editHistoryData, setEditHistoryData] = useState(null);
  const [humanScoresData, setHumanScoresData] = useState(null);

  useEffect(() => {
    console.log("Percent Human: Sidebar loaded")
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.message === "showSidebar") {
        console.log("Percent Human: Sidebar called")

        const appSwitcherButton = document.querySelectorAll(
          ".app-switcher-button"
        )
        const simulateMouseEvent = (
          element: Element,
          eventType: string,
          clientX: number,
          clientY: number
        ) => {
          element.dispatchEvent(
            new MouseEvent(eventType, {
              view: window,
              bubbles: true,
              cancelable: true,
              clientX,
              clientY,
              button: 0
            })
          )
        }
        const buttonRect = appSwitcherButton[0].getBoundingClientRect()
        const buttonLeft = buttonRect.left + 1
        const buttonTop = buttonRect.top + 1
        simulateMouseEvent(
          appSwitcherButton[0],
          "mousedown",
          buttonLeft,
          buttonTop
        )
        simulateMouseEvent(
          appSwitcherButton[0],
          "mouseup",
          buttonLeft,
          buttonTop
        )
        const help = document.querySelector<HTMLInputElement>(
          ".companion-about-panel-button"
        )
        help.style.display = "none"
        setShowSidebar(true)
        const appSwitcher = document.querySelector<HTMLInputElement>(
          ".app-switcher-button-selected"
        )
        appSwitcher.classList.remove("app-switcher-button-selected")
      }
    })

    const fetchHumanScoresData = async () => {
      try {
        const response = await fetch('https://percenthuman.app/v3/scores');
        const data = await response.json();
        setHumanScoresData(data);
      } catch (error) {
        console.error('Error fetching human scores data:', error);
      }
    };
    // click:cOuCgd; mousedown:UX7yZ; mouseup:lbsD7e; mouseenter:tfO1Yc; mouseleave:JywGue; touchstart:p6p2H; touchmove:FwuNnf; touchend:yfqBxc; touchcancel:JMtRjd; focus:AHmuwe; blur:O22p3e; contextmenu:mg9Pef;mlnRJb:fLiPzd;
  }, [])
  const data = {
    labels: ["Overall Document Score"],
    datasets: [
      {
        data: [69, 100 - 69],
        backgroundColor: ["#864be4", "#f2f2f2"],
        hoverBackgroundColor: ["#864be4", "#f2f2f2"]
      }
    ]
  }
  const options = {
    cutout: 60,
    maintainAspectRatio: false,
    plugins: {
      doughnutlabel: {
        labels: [
          {
            text: "69%",
            // font: {
            //   size: "24",
            //   family: "Open Sans, sans-serif",
            //   style: "italic",
            //   weight: "bold"
            // }
          }
        ]
      },
      tooltips: { enabled: false },
      legend: { display: false }
    }
    // options: {
    //   overrides: { legend: { display: false },  }
    // }
  }

  return (
    <div className="flex z-[1000] h-screen w-[300px] flex-col bg-gray-50 font-open-sans">
      <div className="border-b-1 flex flex-row items-center justify-between border-b-gray-600 bg-white py-2 px-3">
        <div className="inline-flex items-center">
          <img className="mr-3 h-6 w-6" src={iconLogo} alt="logo" />
          <span className="text-lg font-semibold text-gray-700">
            {" "}
            Percent Human{" "}
          </span>
        </div>
        <div className="flex items-center space-x-1.5 text-gray-600">
          <button className="p-1.5 hover:rounded-full hover:bg-gray-300">
            <svg
              className="h-5 w-5 text-fuchsia-700"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="1.5"
              stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25M9 16.5v.75m3-3v3M15 12v5.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
              />
            </svg>
          </button>
          <button className="p-1 hover:rounded-full hover:bg-gray-300">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              strokeWidth="1.5"
              stroke="currentColor"
              className="h-6 w-6">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>
      <div className="results flex flex-col space-y-5 overflow-y-auto px-3 py-5 text-gray-900">
        <div className="flex relative flex-col justify-center space-y-3 rounded-3xl bg-white p-2 px-4 py-4 shadow-lg">
          <span className="text-center text-xl font-semibold">
            Authenticy Report
          </span>
          <Doughnut
            height="150px"
            width="150px"
            options={options}
            data={data}
          />
          <span className="text-md pb-3 text-center text-gray-600">
            Our analysis considers the text to be mostly human generated.
          </span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            className="absolute bottom-2 right-2 h-5 w-5 text-gray-600">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
            />
          </svg>
        </div>
        <div className="flex relative flex-col justify-center space-y-3 rounded-3xl bg-white p-2 px-2 py-4 shadow-lg">
          <span className="text-center text-xl font-semibold">Subscores</span>
          <div className="px-y grid grid-cols-2 items-start gap-x-2">
            <div className="flex flex-col items-center justify-center space-y-2 px-2 pb-3">
              <span className="percent-human-label text-center text-sm font-semibold">
                Perplexity
              </span>
              <div className="h-6 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  className="percent-human-bar h-6 rounded-full bg-gradient-to-b from-red-300 to-red-400"
                  style={{ width: "33%" }}
                />
              </div>
              <span className="ai-feedback-temp text-center text-sm font-normal text-gray-600">
                <span className="font-semibold text-fuchsia-500">12.8 </span>
                Perplex Score
              </span>
            </div>
            <div className="flex flex-col items-center justify-center space-y-2 px-2 pb-3">
              <span className="percent-human-label text-center text-sm font-semibold">
                AI Content
              </span>
              <div className="h-6 w-full rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  className="percent-human-bar h-6 rounded-full bg-gradient-to-b from-green-300 to-green-400"
                  style={{ width: "77%" }}
                />
              </div>
              <span className="ai-feedback-temp text-center text-sm font-normal text-gray-600">
                <span className="font-semibold text-fuchsia-500">67%</span>{" "}
                Human Text
              </span>
            </div>
          </div>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            className="absolute bottom-2 right-2 h-5 w-5 text-gray-600">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
            />
          </svg>
        </div>
        <div className="flex flex-col justify-center space-y-3 rounded-3xl bg-white p-2 px-4 py-4 shadow-lg">
          <span className="text-center text-xl font-semibold">
            Contributors
          </span>
          <div className="flex flex-row items-end space-x-5 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-200 scrollbar-track-white scrollbar-thumb-rounded-xl pb-2">
            <div className="flex flex-col items-center justify-center space-y-1.5">
              <span className="text-center text-sm text-gray-600">
                T.Demarcus
              </span>
              <img
                src="https://www.w3schools.com/howto/img_avatar.png"
                alt="Avatar"
                className="h-16 w-16 rounded-full"
              />
              <span className="text-md text-center font-semibold">47m</span>
            </div>
            <div className="flex flex-col items-center justify-center space-y-1.5">
              <span className="text-center text-sm text-gray-600">
                P.Sanborn
              </span>
              <img
                src="https://www.w3schools.com/w3images/avatar6.png"
                alt="Avatar"
                className="h-12 w-12 rounded-full"
              />
              <span className="text-md text-center font-semibold">12m</span>
            </div>
            <div className="flex flex-col items-center justify-center space-y-1.5">
              <span className="text-center text-sm text-gray-600">
                A.Sanborn
              </span>
              <img
                src="https://www.w3schools.com/howto/img_avatar2.png"
                alt="Avatar"
                className="h-10 w-10 rounded-full"
              />
              <span className="text-md text-center font-semibold">3m</span>
            </div>
            <div className="flex flex-col items-center justify-center space-y-1.5">
              <span className="text-center text-sm text-gray-600">Ur.Mom</span>
              <img
                src="https://www.w3schools.com/w3images/avatar5.png"
                alt="Avatar"
                className="h-8 w-8 rounded-full"
              />
              <span className="text-md text-center font-semibold">1m</span>
            </div>
          </div>
        </div>
        <div className="flex relative flex-col justify-center space-y-3 rounded-3xl bg-white p-2 px-4 py-4 shadow-lg">
          <span className="text-center text-xl font-semibold">
            Writing Sessions
          </span>
          <span className="text-md pb-3 text-center font-normal text-gray-600">
            <span className="font-bold text-fuchsia-500">12 sessions</span> over{" "}
            <span className="font-bold text-fuchsia-500">3 days</span> with an
            average of{" "}
            <span className="font-bold text-fuchsia-500">102 edits</span> per
            session.
          </span>
          {/* <span class="pb-1 text-center text-xs text-gray-600">A distinct session is defined as 10 mintues between edits.</span> */}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            className="absolute bottom-2 right-2 h-5 w-5 text-gray-600">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
            />
          </svg>
        </div>
        <button className="text-md inline-flex items-center justify-center rounded-3xl p-2 px-4 text-center font-semibold bg-white text-gray-700 shadow-lg hover:bg-gray-200">
          <svg
            className="mr-4 h-5 w-5 text-fuchsia-700"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25M9 16.5v.75m3-3v3M15 12v5.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
            />
          </svg>
          View more stats
        </button>
      </div>
    </div>
  )
}
export default AnalysisSidebar
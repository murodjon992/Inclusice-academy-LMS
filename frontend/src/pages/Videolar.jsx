import React, { useState, useEffect } from 'react'
import { fmtDate, truncate, Linebreaks } from '../lib/helpers'
import { useAuth } from '../lib/auth'
import { useApi } from '../lib/hooks'
import { api, errorText } from '../lib/api'
import { Async, Hero, Spinner, NotFound } from '../components/ui'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'

export default function Videolar() {
  const state = useApi('/videolar/')
  const kategoriyalar = state.data || []
  return (
    <><style>{`
    .custom-scroll {
        overflow-x: auto;
        white-space: nowrap;
        display: flex;
        -webkit-overflow-scrolling: touch;
        padding-bottom: 15px;
    }
    .custom-scroll::-webkit-scrollbar {
        height: 8px;
    }
    .custom-scroll::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    .custom-scroll::-webkit-scrollbar-thumb {
        background: #b1b1b1;
        border-radius: 10px;
    }
    .flex-shrink-0 {
        flex-shrink: 0 !important;
    }
    .text-siyoh {
        color: #4B0082; /* Siyoh rang */
        font-weight: 600;
        margin-top: 30px;
    }
    hr {
        border-top: 2px solid #ccc;
        width: 50%; /* Rasmdagidek chiziq yarmi bo'lishi uchun */
        margin-left: 0;
    }
`}</style><div className="custom-breadcrumns border-bottom"><div className="bg-siyoh"><div className="container"><div style={{minHeight: "250px"}} className="d-flex py-5 flex-column align-items-center justify-content-center"><h1 className="text-light pt-5 mt-5">VIDEOLAR</h1></div></div></div></div><div className="container-fluid mt-5">{(kategoriyalar || []).map((cat, _i1) => (<React.Fragment key={_i1}> {cat?.videos ? (<><div className={`category-section mb-5 p-1 ${(_i1 + 1) % 2 === 1 ? 'odd-bg' : ''}`}><div className="container"><h3 className="text-siyoh m-0 p-0">{cat?.name}</h3><div className="row flex-nowrap custom-scroll mx-0">{(cat?.videos || []).map((video, _i2) => (<React.Fragment key={_i2}><div className="col-10 col-md-4 col-lg-3 flex-shrink-0 px-2"><div className="video-container my-3">{video?.video_type === 'url' ? (<><iframe style={{borderRadius: "8px"}} width="100%" height="180" src={video?.embed_url} title={video?.title} frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerPolicy="strict-origin-when-cross-origin" allowFullScreen></iframe></>) : (<><video width="100%" height="180" controls style={{borderRadius: "8px", background: "#000"}}><source src={video?.video_file} /></video></>)}</div><p className="text-muted small text-truncate m-0 p-0">{video?.title}</p></div></React.Fragment>))}</div><hr /></div></div></>) : null} </React.Fragment>))}</div></>
  )
}

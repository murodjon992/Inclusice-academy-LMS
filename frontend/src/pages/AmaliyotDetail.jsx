import React, { useState, useEffect } from 'react'
import { fmtDate, truncate, Linebreaks } from '../lib/helpers'
import { useAuth } from '../lib/auth'
import { useApi } from '../lib/hooks'
import { api, errorText } from '../lib/api'
import { Async, Hero, Spinner, NotFound } from '../components/ui'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'

export default function AmaliyotDetail() {
  const { turSlug, itemSlug } = useParams()
  const state = useApi(`/amaliyot/${turSlug}/${itemSlug}/`)
  const item = state.data
  if (state.loading) return <Spinner />
  if (state.error) return <NotFound />
  return (
    <><style>{`
    .oquv{
        position: relative;
    }
    .oquv::after{
    content: " ";
    height: 80px;
    width:2px;
    background: purple;
    position:absolute;
    right: 20px;
    top: 0;

    }
`}</style><div className="custom-breadcrumns border-bottom"><div className="container"><a href="/">Home</a>{' '}<span className="mx-3 icon-keyboard_arrow_right"></span>{' '}<a href="/courses/">Courses</a>{' '}<span className="mx-3 icon-keyboard_arrow_right"></span>{' '}<span className="current">Courses</span></div></div><div className="site-section"><div className="container"><div className="row"><div className="col-12"><img width="100%" className="m-0 p-0" height="400" style={{objectFit: "cover"}} src={item?.image} alt="" /></div></div><div className="row m-0 p-0"><div className="col-9 mt-3 shadow"><div className="card my-3"><h1 className="card-title text-black pl-4">{item?.title}</h1><p className="text-black pl-4">{item?.turi?.nomi}</p><div className="card-body"><div className="row"><div className="col-6 oquv"><h4 className="text-black">O'quvchilarga yordam beradi</h4><ul>{(item?.helps || []).map((h, _i1) => (<React.Fragment key={_i1}> {h?.help_type === 'pupil' ? (<><li>{h?.text}</li></>) : null} </React.Fragment>))}</ul></div><div className="col-6"><h4 className="text-black">O'qituvchilarga yordam beradi</h4><ul>{(item?.helps || []).map((h, _i2) => (<React.Fragment key={_i2}> {h?.help_type === 'teacher' ? (<><li>{h?.text}</li></>) : null} </React.Fragment>))}</ul></div></div></div></div><div className="card p-3 text-black mb-3"><p>{item?.description}</p><hr />{(item?.videos || []).map((i, _i3) => (<React.Fragment key={_i3}><div className="d-flex justify-content-between"><div className="left"><h2>{i?.title}</h2><h4>Amaliyot qanday ishlaydi</h4><p>Videoni tomosha qiling va ko'proq ma'lumot olin</p><small>Davomiyligi: {i?.duration}</small></div><div className="right">{i?.video_type === 'url' ? (<><iframe style={{borderRadius: "8px"}} width="100%" height="180" src={i?.embed_url} title={i?.title} frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerPolicy="strict-origin-when-cross-origin" allowFullScreen></iframe></>) : (<> {i?.video_file ? (<><video width="100%" height="180" controls style={{borderRadius: "8px", background: "#000"}}><source src={i?.video_file} /></video></>) : null} </>)}</div></div><hr /></React.Fragment>))} {(item?.sections || []).map((i, _i4) => (<React.Fragment key={_i4}><h3>{i?.title}</h3><p>{i?.content}</p><hr /></React.Fragment>))}</div></div><div style={{height: "300px"}} className="col-3 mt-3 shadow"><div className="card p-2 my-3"><h5 className="text-black">Ta'lim Jarayoni</h5><img src="/static/images/siklp.png" alt="" /></div></div></div></div></div></>
  )
}

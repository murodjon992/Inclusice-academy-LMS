import React, { useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Async } from '../components/ui'
import { Linebreaks } from '../lib/helpers'
import { useApi } from '../lib/hooks'
import { useAuth } from '../lib/auth'
import { api, errorText } from '../lib/api'

function Lesson({ lesson, enrolled, active, onPlay }) {
  const icon = lesson.locked ? 'fa-lock' : lesson.completed ? 'fa-check-circle' : 'fa-play-circle'
  return (
    <li className="list-group-item d-flex justify-content-between align-items-center py-3">
      <div className="flex-grow-1">
        {lesson.has_video ? (
          <>
            <button type="button" disabled={lesson.locked} onClick={() => onPlay(lesson)}
              className="lesson-btn btn btn-link text-siyoh p-0 font-weight-bold text-left">
              <i className={`fa ${icon} mr-2`}></i>{lesson.title}
            </button>
            {active && lesson.content && (
              <div className="lesson-content mt-2 text-muted small"><Linebreaks text={lesson.content} /></div>
            )}
          </>
        ) : (
          <span className="text-dark">
            <i className="fa fa-file-alt mr-2"></i> {lesson.title}{' '}
            {lesson.locked ? (
              <span className="text-muted small"><i className="fa fa-lock"></i> (Kursga yoziling)</span>
            ) : lesson.pdf ? (
              <>
                <a href={lesson.pdf} rel="noopener noreferrer" target="_blank">ko'rish</a>
                <iframe src={`${lesson.pdf}#toolbar=0`} title={lesson.title} width="100%" height="600px"></iframe>
              </>
            ) : lesson.content ? (
              <div className="text-muted small"><Linebreaks text={lesson.content} /></div>
            ) : (
              <span className="text-muted small">(Fayl Yuklanmagan)</span>
            )}
          </span>
        )}
      </div>
      {enrolled && lesson.pdf && (
        <a href={lesson.pdf} download className="btn btn-sm btn-light border ml-2">
          <i className="fa fa-download text-info"></i> PDF
        </a>
      )}
    </li>
  )
}

function Detail({ data, reload }) {
  const { user } = useAuth()
  const { course, modules, enrolled, quiz, quiz_result: quizResult } = data
  const [progress, setProgress] = useState(data.progress)
  const [closed, setClosed] = useState({})
  const [current, setCurrent] = useState(null)
  const [error, setError] = useState('')
  const sent = useRef(new Set())

  const enroll = async () => {
    setError('')
    try {
      await api(`/courses/${course.id}/enroll/`, { method: 'POST' })
      reload()
    } catch (e) { setError(errorText(e)) }
  }

  // Videoning 80% i ko'rilganda dars tugagan deb belgilanadi
  const onTime = (e) => {
    const v = e.target
    if (!enrolled || !current || !v.duration || sent.current.has(current.id)) return
    if (v.currentTime / v.duration >= 0.8) {
      sent.current.add(current.id)
      api(`/lessons/${current.id}/complete/`, { method: 'POST' })
        .then((r) => { setProgress(r.progress); reload() })
        .catch(() => sent.current.delete(current.id))
    }
  }

  return (
    <>
      <style>{`.tugma:hover{background-color:#3a0ca3;color:#fff !important;}`}</style>
      <div className="custom-breadcrumns border-bottom">
        <div className="container">
          <a href="/">Home</a>
          <span className="mx-3 icon-keyboard_arrow_right"></span>
          <a href="/courses/">Courses</a>
          <span className="mx-3 icon-keyboard_arrow_right"></span>
          <span className="current">Courses</span>
        </div>
      </div>
      <div className="site-section">
        <div className="container">
          <div className="row">
            <div className="col-lg-4 mb-4">
              <div className="card shadow-sm border-0">
                {course.image && <img width="100%" src={course.image} className="card-img-top" alt={course.title} />}
                <div className="card-body">
                  <h4 className="h5 font-weight-bold text-siyoh">{course.title}</h4>
                  <p className="small text-muted mb-3"><i className="fa fa-clock"></i> {course.duration} min</p>
                  {user ? (
                    enrolled ? (
                      <>
                        <div className="mb-3">
                          <div className="d-flex justify-content-between mb-1">
                            <span className="small font-weight-bold">Jarayon:</span>
                            <span className="small font-weight-bold">{progress}%</span>
                          </div>
                          <div className="progress" style={{ height: '8px' }}>
                            <div className="progress-bar bg-siyoh" style={{ width: `${progress}%` }}></div>
                          </div>
                        </div>
                        <span className="badge bg-warning text-dark w-100 py-2">Siz kursga yozilgansiz</span>
                      </>
                    ) : (
                      <button type="button" onClick={enroll} className="btn bg-siyoh text-white w-100">Kursga yozilish</button>
                    )
                  ) : (
                    <a href={`/login-user/?next=/course-detail/${course.slug}/`} className="btn btn-outline-info w-100">Kirish va o'qish</a>
                  )}
                  {error && <div className="form-error">{error}</div>}
                </div>
              </div>
              <a href="/#courseDetail" className="btn btn-light mt-3"><i className="fas fa-arrow-left"></i> Orqaga</a>
            </div>
            <div className="col-lg-8">
              <div className="accordion shadow-sm">
                {modules.map((m) => (
                  <div className="card border-bottom" key={m.id}>
                    <div className="card-header bg-white py-3" style={{ cursor: 'pointer' }}
                      onClick={() => setClosed((c) => ({ ...c, [m.id]: !c[m.id] }))}>
                      <h5 className="mb-0 text-siyoh d-flex justify-content-between align-items-center">
                        <span><i className={`fa fa-chevron-${closed[m.id] ? 'right' : 'down'} small mr-2`}></i> {m.title}</span>
                      </h5>
                    </div>
                    {!closed[m.id] && (
                      <div className="card-body p-0">
                        <ul className="list-group list-group-flush">
                          {m.lessons.map((l) => (
                            <Lesson key={l.id} lesson={l} enrolled={enrolled} active={current && current.id === l.id}
                              onPlay={setCurrent} />
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
              {enrolled && (
                <div className="mt-4 shadow-sm bg-white p-3 rounded">
                  {current && current.video && (
                    <video key={current.id} controls autoPlay width="100%" className="rounded shadow" onTimeUpdate={onTime}>
                      <source src={current.video} type="video/mp4" />
                    </video>
                  )}
                  {progress === 100 && quiz && (
                    <div className="mt-3 text-center">
                      <a href={`/course-test/${course.id}/`} className="btn btn-success btn-lg px-5 shadow">
                        {quizResult ? "Natijani ko'rish" : 'Imtihonni topshirish'}
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default function CourseDetail() {
  const { slug } = useParams()
  const { user } = useAuth()
  const state = useApi(`/courses/${slug}/?u=${user ? user.id : 0}`)
  return <Async state={state}>{(data) => <Detail key={data.course.id + ':' + (data.enrolled ? 1 : 0)} data={data} reload={state.reload} />}</Async>
}

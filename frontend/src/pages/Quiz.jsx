import React, { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Async } from '../components/ui'
import { useApi } from '../lib/hooks'
import { useAuth } from '../lib/auth'
import { api, errorText } from '../lib/api'

const css = `
.hover-effect:hover{background-color:#f8f9fa;border-color:#3a0ca3 !important;cursor:pointer;}
.custom-control-input:checked ~ .custom-control-label{color:#3a0ca3;font-weight:bold;}
`

// Ikkala test sahifasi (mustaqil test va kurs yakuniy testi) uchun umumiy forma
function QuizForm({ quiz, questions, onSubmit }) {
  const [answers, setAnswers] = useState({})
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try { await onSubmit(answers) } catch (err) { setError(errorText(err)); setBusy(false) }
  }

  return (
    <>
      <style>{css}</style>
      <div className="container mt-5 pt-5">
        <div className="card shadow-sm p-4">
          <h2 className="text-siyoh border-bottom pb-3">{quiz.title}</h2>
          <p className="text-muted">Minimal o'tish ko'rsatkichi: <strong>{quiz.min_percentage}%</strong></p>
          <form onSubmit={submit}>
            {questions.map((q, qi) => (
              <div className="card mb-4 shadow-sm border-0 rounded-lg" key={q.id}>
                <div className="card-body">
                  <h5 className="font-weight-bold mb-3">
                    <span className="text-siyoh">{qi + 1}.</span> {q.text}
                  </h5>
                  <div className="options-group">
                    {q.answers.map((a) => (
                      <div className="custom-control custom-radio mb-2 p-2 border rounded hover-effect" key={a.id}>
                        <input type="radio" id={`ans_${a.id}`} name={`question_${q.id}`} value={a.id}
                          className="custom-control-input" required checked={answers[q.id] === a.id}
                          onChange={() => setAnswers((x) => ({ ...x, [q.id]: a.id }))} />
                        <label className="custom-control-label d-block ml-4" htmlFor={`ans_${a.id}`}>{a.text}</label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
            {error && <div className="alert alert-danger">{error}</div>}
            <div className="text-center my-5">
              <button type="submit" disabled={busy} className="btn bg-siyoh text-light btn-lg px-5 shadow">
                Testni yakunlash va natijani ko'rish
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  )
}

// /test/:testId  (mustaqil test; ko'rish hammaga ochiq, topshirish uchun kirish kerak)
export function QuizPage() {
  const { testId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const state = useApi(`/quizzes/${testId}/`)
  return (
    <Async state={state}>
      {({ quiz, questions }) => (
        <QuizForm quiz={quiz} questions={questions} onSubmit={async (answers) => {
          if (!user) { navigate(`/login-user/?next=/test/${testId}`); return }
          await api(`/quizzes/${testId}/submit/`, { method: 'POST', body: { answers } })
          navigate(`/test-result/${testId}/`)
        }} />
      )}
    </Async>
  )
}

// /course-test/:courseId  (kurs 100% tugagach, faqat bir marta)
export function CourseTestPage() {
  const { courseId } = useParams()
  const navigate = useNavigate()
  const state = useApi(`/courses/${courseId}/test/`)
  if (state.error && state.error.status === 403) {
    const slug = state.error.data && state.error.data.slug
    return (
      <div className="container py-5 my-5 text-center">
        <h3 className="text-siyoh">Avval kursni tugating</h3>
        {slug && <a href={`/course-detail/${slug}/`} className="btn bg-siyoh text-light mt-3">Kursga qaytish</a>}
      </div>
    )
  }
  return (
    <Async state={state}>
      {(data) => {
        if (data.already_done) { navigate(`/test-result/${data.quiz_id}/`, { replace: true }); return null }
        return (
          <QuizForm quiz={data.quiz} questions={data.questions} onSubmit={async (answers) => {
            const r = await api(`/courses/${courseId}/test/`, { method: 'POST', body: { answers } })
            navigate(`/test-result/${r.result.quiz}/`)
          }} />
        )
      }}
    </Async>
  )
}

export function TestResultPage() {
  const { quizId } = useParams()
  const state = useApi(`/quizzes/${quizId}/result/`)
  return (
    <Async state={state}>
      {({ result }) => (
        <div className="site-section">
          <div className="container pt-5">
            <h2>{result.quiz_title}</h2>
            <p className="fs-4">Sizning natijangiz: <b>{result.score}%</b></p>
            {result.passed ? (
              <div className="alert alert-success">🎉 Tabriklaymiz! Siz testdan o‘tdingiz.</div>
            ) : (
              <div className="alert alert-danger">❌ Afsus, siz testdan o‘ta olmadingiz.</div>
            )}
            <a href={`/course-detail/${result.course_slug}/`} className="btn btn-primary mt-3">Kursga qaytish</a>{' '}
            <a href="/user-dashboard/" className="btn btn-info mt-3">Profilga</a>
          </div>
        </div>
      )}
    </Async>
  )
}

import { useContext } from "react"
import { DashboardContext } from "./DashboardContext"

export default function Row({ key, courseId }) {

    const {getCourseByCourseId} = useContext(DashboardContext)
    const course = getCourseByCourseId(courseId)

    console.log(course,  course['Course ID'])
    return (
        <div>
            {`${course['Course name']}`}
        </div>
    )
}
// 页面加载完成后执行的函数
window.onload = function() {
    // 示例：为所有具有 'btn' 类的按钮添加点击事件监听器，当点击时改变按钮的背景颜色
    var buttons = document.querySelectorAll('.btn');
    buttons.forEach(function(button) {
        button.addEventListener('click', function() {
            this.style.backgroundColor = '#0056b3';
        });
    });

    // 示例：当在某个输入框获得焦点时，改变输入框的边框颜色
    var inputs = document.querySelectorAll('input');
    inputs.forEach(function(input) {
        input.addEventListener('focus', function() {
            this.style.borderColor = '#007BFF';
        });
        input.addEventListener('blur', function() {
            this.style.borderColor = '#ccc';
        });
    });

    // 示例：在学生选题页面，当选择题目后，显示所选题目相关的详细描述（假设题目数据存储在一个名为 'topics' 的全局变量中，这里只是示例，实际需从后端获取）
    if (window.location.href.includes('student/topic_selection.html')) {
        var topicSelect = document.getElementById('topic_id');
        topicSelect.addEventListener('change', function() {
            var selectedTopicId = this.value;
            var selectedTopic = topics.find(function(topic) {
                return topic.topic_id === selectedTopicId;
            });
            if (selectedTopic) {
                var descriptionElement = document.createElement('p');
                descriptionElement.textContent = selectedTopic.description;
                document.body.appendChild(descriptionElement);
            }
        });
    }

    if (window.location.href.includes('student/topic_selection.html'))  {
        var submitButton = document.querySelector('input[type="submit"]');
        submitButton.addEventListener('click', function() {
             var studentTopicId = document.getElementById('student_topic_id').value;
             if (!studentTopicId.match(/^400\d$/)) {
                   alert('学生编号格式不正确，请按照格式：400x 填写');
                    return;
              }

        // 这里可以继续添加对其他输入框（如group_members）的格式校验逻辑

        // 如果格式都正确，允许表单提交
          this.form.submit();
    });
};
    // 示例：在教师上传资料页面，当选择文件后，显示所选文件的名称（只是简单示例，实际可能需要更多处理）
    if (window.location.href.includes('teacher/material_upload.html')) {
        var fileInput = document.getElementById('material_file');
        fileInput.addEventListener('change', function() {
            var file = this.files[0];
            if (file) {
                var fileLabel = document.getElementById('material_file_label');
                if (!fileLabel) {
                    fileLabel = document.createElement('label');
                    fileLabel.id = 'material_file_label';
                    fileLabel.textContent = '已选择文件：' + file.name;
                    document.body.appendChild(fileLabel);
                } else {
                    fileLabel.textContent = '已选择文件：' + file.name;
                }
            }
        });
    }
};


document.addEventListener('DOMContentLoaded', function () {
    const queryButton = document.getElementById('query-button');
    const resultContainer = document.getElementById('result-container');

    queryButton.addEventListener('click', function () {
        // 发送AJAX请求到后端查询成绩
        const xhr = new XMLHttpRequest();
        xhr.open('post', '{{ url_for(\'student_score_query\') }}', true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.score) {
                    document.getElementById('score-value').textContent = response.score;
                    resultContainer.style.display = 'block';
                } else {
                    document.getElementById('no-result-message').textContent = "成绩尚未公布，请耐心等待。";
                    resultContainer.style.display = 'block';
                }
            }
        };
        xhr.send();
    });
});
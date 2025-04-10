package newsplatform.models;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.Date;
import java.util.List;

@Document(collection = "users")
public class User {
    
    @Id
    private String userId;

    private String pw;
    private String name;
    private Date signupDate;
    private String vocabularyLevel;
    private List<String> seenWords;

    public User() {}

    public User(String userId, String pw, Date signDate, String vocabularyLevel, List<String> seenWords ) {
        this.userId = userId;
        this.pw = pw;
        this.signupDate = signDate;
        this.vocabularyLevel = vocabularyLevel;
        this.seenWords = seenWords;
    }


    public String getUserId() {return userId; }
    public void setUserId(String userId) {this.userId = userId;}
    
    public String getPw() {return pw; }
    public void setPw(String pw) { this.pw = pw; }

    public Date getSigupDate() { return signupDate; }
    public void setSignupDate(Date signupDate ) { this.signupDate = signupDate; }

    public String getVocabularyLevel() {return vocabularyLevel; }
    public void setVocabularyLevel(String vocabularyLevel) { this.vocabularyLevel = vocabularyLevel; }

    public List<String> getSeenWords() { return seenWords; }
    public void setSeenWords(List<String> seenWords) { this.seenWords = seenWords;}


    
}